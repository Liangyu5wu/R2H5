import h5py
import numpy as np
import ROOT
import importlib
import logging
import os
import cppyy
import r2h5
import subprocess
import tracemalloc
from datetime import datetime

class DatasetConverter:
    def __init__(self, config, save_intermediate=False, overwrite_existing_output_files=False):
        self._start_memory_monitor()
        self._log_memory_snapshot()
        self.config = config
        self.root_file_list = config["input"]["root_file_list"]
        self.output_path = config["output"]["h5_path"]
        self.save_intermediate = save_intermediate
        self.overwrite_existing_output_files = overwrite_existing_output_files
        self.df_list = None
        logging.info(f"Writing output path: {self.output_path}")
        logging.debug(f"Input ROOT files:")
        for root_file in self.root_file_list:
            logging.debug(f"    {root_file}")
        if len(self.root_file_list) == 0:
            logging.error("No input ROOT files found. Please check that your input file paths exist!")
            exit(1)
        os.makedirs(self.output_path, exist_ok=True)

    def format_ntuples(self, n_threads=8, max_events_per_file=None):
        """Format ROOT files to RDataFrame."""
        # Set up multithreading
        if n_threads > 1:
            logging.info(f"Enabling implicit multithreading with {n_threads} threads")
            ROOT.ROOT.EnableImplicitMT(n_threads)

        self._log_memory_snapshot()
        # Compile ROOT macros
        for macro in self.config.get("cpp_helpers", []):
            logging.info(f"Compiling cpp_helper file {macro}")
            macro = f"{__package__}/cpp_helpers/{macro}"
            if not os.path.exists(macro):
                logging.warning(f"File {macro} does not exist.")
                continue
            ROOT.gInterpreter.Declare(f'#include "{macro}"')

        self._log_memory_snapshot()
        df_list = []
        N_files = len(self.root_file_list)
        logging.info(f"Creating RDataFrame from {N_files} files")
        for root_file in self.root_file_list:
            logging.debug(f"Adding file {root_file}")
            df = ROOT.RDataFrame(self.config["input"]["tree_name"], root_file)
            if max_events_per_file:
                if max_events_per_file < 1:
                    logging.warning(f"max_events is {max_events}. Must be greater than 0! Skipping dataframe.")
                    continue
                logging.info(f"Limiting to {max_events_per_file} events per file")
                df = df.Range(0, max_events_per_file)
            df_list.append(df)
        
        self._log_memory_snapshot()
        # Apply branch definitions from config
        for rdf_define in self.config.get("rdf_defines", []):
            module_path, function_name = rdf_define.split(".")
            module_path = f"{__package__}.rdf_defines.{module_path}"
            module = importlib.import_module(module_path)
            logging.info(f"Applying RDF define {module_path}.{function_name}")
            try:
                module = importlib.import_module(module_path)
            except ImportError as e:
                logging.error(f"Could not import {module_path}: {e}")
                exit(1)
            module_function = getattr(module, function_name)
            for i_file, df in enumerate(df_list):
                df_list[i_file] = module_function(df)

        self.df_list = df_list

    def run(self, file_index_offset=0):
        """Run the conversion."""
        # Check if ROOT files were previously formatted
        if self.df_list is None:
            logging.info("Formatting ROOT files was not previously run. Consider doing this first.")
            self.format_ntuples()

        # Convert ROOT files to H5
        for i_df, df in enumerate(self.df_list):
            logging.info(f"Converting ROOT file {i_df+1+file_index_offset} of {len(self.df_list)+file_index_offset}")
            self._log_memory_snapshot()
            self._root_to_h5(
                df=df,
                output_file_name=os.path.join(self.output_path, f"output_{i_df+file_index_offset:03}.h5")
            )
        #self._plot_memory_profile(file_index_offset=file_index_offset)

    def submit_batch(self, config_path, batch_system, dry_run=False, debug=False):
        """Submit conversion to batch system."""
        if batch_system == "slurm":
            logging.info("Submitting to SLURM")
            slurm_path = f"{r2h5.__package_path__}/r2h5/slurm/{os.path.splitext(os.path.basename(config_path))[0]}"
            os.makedirs(slurm_path, exist_ok=True)
            os.makedirs(f"{slurm_path}/logs", exist_ok=True)
            os.makedirs(f"{slurm_path}/submission", exist_ok=True)
            logging.info(f"Writing SLURM submission files to {slurm_path}")
            self.config['batch'] = self.config.get("batch", {})
            max_files = self.config['batch'].get("max_files", -1)
            for i_df in range(len(self.root_file_list)):
                if max_files>0 and i_df >= max_files:
                    logging.info(f"Reached maximum number of files to process: {max_files}")
                    break
                if not self.overwrite_existing_output_files:
                    output_file_name = os.path.join(self.output_path, f"output_{i_df:03}.h5")
                    if os.path.exists(output_file_name):
                        logging.info(f"Output file {output_file_name} already exists. Skipping batch submission.")
                        continue
                job_name = f"{self.config['batch'].get('batch_name','r2h5')}_{i_df:03}"
                slurm_submission_file = r2h5.get_slurm_script(
                    job_name=job_name,
                    config_path=config_path,
                    debug=debug,
                    file_name=self.root_file_list[i_df],
                    file_index_offset=i_df,
                    job_path=slurm_path, 
                    time=self.config["batch"].get("time", "00:30:00"),
                    memory=self.config["batch"].get("memory", 4),
                    partition=self.config["batch"].get("partition", "roma"),
                    account=self.config["batch"].get("account", "atlas:usatlas"),
                    cpu_count=self.config["batch"].get("cpu_count", 1),
                )
                logging.debug(f"    file {job_name}.sh")
                with open(f"{slurm_path}/submission/{job_name}.sh", "w") as f:
                    f.write(slurm_submission_file)
                if not dry_run:
                    command = f"sbatch {slurm_path}/submission/{job_name}.sh"
                    logging.debug(f"Submitting job {i_df} with command {command}")
                    subprocess.run(f"sbatch {slurm_path}/submission/{job_name}.sh", shell=True, check=False)

        elif batch_system == "condor":
            logging.info("Submission to HTCondor not implemented yet :D")
        else:
            logging.error(f"Batch system {batch_system} not recognized.")
            exit(1)
        logging.info("Submitted all jobs to batch system")

    def delete_incomplete_output_files(self, dry_run=False):
        """Delete output files that do not have the expected data features in the output."""
        file_status = {"good": 0, "incomplete": 0, "corrupted": 0, 'notfound': 0}
        if dry_run: logging.info("Running in dry run mode. No files will be deleted.")
        for i_df in range(len(self.root_file_list)):
            logging.debug(f"Checking output file {i_df+1} of {len(self.root_file_list)}")
            output_file_name = os.path.join(self.output_path, f"output_{i_df:03}.h5")
            # Openn h5 file and check if it has the expected data features
            if not os.path.exists(output_file_name):
                logging.debug(f" -> file {output_file_name} does not exist!")
                file_status["notfound"] += 1
                continue
            try:
                with h5py.File(output_file_name, "r") as h5f:
                    good = True
                    # Check if the file has the expected data features
                    for object_name, object_config in self.config.get("Objects", {}).items():
                        if object_name not in h5f:
                            logging.debug(f" -> does not contain {object_name}. Deleting it.")
                            file_status["incomplete"] += 1
                            good = False
                            if not dry_run: os.remove(output_file_name)
                            break
                    for objcol_name, objcol_config in self.config.get("ObjectCollections", {}).items():
                        if objcol_name not in h5f:
                            logging.debug(f" -> does not contain {objcol_name}. Deleting it.")
                            file_status["incomplete"] += 1
                            good = False
                            if not dry_run: os.remove(output_file_name)
                            break
                    file_status["good"] += 1 if good else 0
            except:
                logging.debug(f" -> file {output_file_name} is corrupted. Deleting it.")
                file_status["corrupted"] += 1
                if not dry_run: os.remove(output_file_name)
        logging.info(f"File status: {file_status['good']} good, {file_status['incomplete']} incomplete, {file_status['corrupted']} corrupted, {file_status['notfound']} not found")


    """ 
    Private methods for internal data conversion
    """
    def _root_to_h5(self, df, output_file_name):
        """Convert processed ROOT DataFrame to H5 format."""
        logging.info(f"Converting ROOT RDataFrame to H5 file {output_file_name}")
        # Check if the output file already exists
        if os.path.exists(output_file_name):
            if not self.overwrite_existing_output_files:
                logging.info(f"Output file {output_file_name} already exists. Skipping conversion.")
                return
            else:
                logging.info(f"Output file {output_file_name} already exists. Deleting it for overwrite.")
                os.remove(output_file_name)

        with h5py.File(output_file_name, "w") as h5f:
            vector_object_lengths = {}

            # Loop over objects in the config
            for object_name, object_config in self.config.get("Objects", {}).items():
                self._log_memory_snapshot()
                if object_config["source_format"] == "vector":
                    logging.info(f"Converting Object data {object_name} with vector source format to H5")
                    structured_data, object_lengths = self._extract_vector_object(df, object_name, object_config)
                    if object_config.get("store_length", False):
                        vector_object_lengths[object_name] = object_lengths
                    self._save_to_h5(h5f, object_name, structured_data)
                    logging.info(f"Deleting {object_name} extracted data from memory")
                    del structured_data

                elif object_config["source_format"] == "scalar":
                    logging.info(f"Converting Object data {object_name} with scalar source format to H5")
                    structured_data = self._extract_scalar_object(df, object_name, object_config)
                    self._save_to_h5(h5f, object_name, structured_data)

                else:
                    logging.warning(f"Unsupported source_format '{source_format}' for object '{object_name}'")

            # Loop over object collections in the config
            for objcol_name, objcol_config in self.config.get("ObjectCollections", {}).items():
                self._log_memory_snapshot()
                logging.info(f"Converting ObjectCollection data {objcol_name} with vector format to H5")
                self._extract_object_collection(df, objcol_name, objcol_config, vector_object_lengths, h5f)

        logging.info(f"Saved H5 file to {output_file_name}")

    def _extract_vector_object(self, df, object_name, config):
        data = {}
        lengths = None
        selection_branch = config.get("selection")

        for branch in config['branches']:
            logging.info(f"Extracting branch {branch}")
            self._log_memory_snapshot()
            raw = [r2h5.convert_rvec_to_numpy(x) for x in df.AsNumpy(columns=[branch])[branch]]
            if config.get('store_length', False):
                lengths = [len(x) for x in raw]
            data[branch] = np.concatenate(raw)

        if config.get('event_number', False):
            logging.info(f"Duplicating event number data for {object_name} based on Object lengths.")
            self._log_memory_snapshot()
            event_number = df.AsNumpy(columns=["eventNumber"])["eventNumber"]
            repeated = [np.tile(event_number[i], (lengths[i],)) for i in range(len(lengths))]
            data["eventNumber"] = np.concatenate(repeated)

        structured = self._build_structured_array(data)
        return structured, lengths

    def _extract_scalar_object(self, df, object_name, config):
        data = {}
        for branch in config['branches']:
            logging.debug(f"Extracting branch {branch}")
            data[branch] = df.AsNumpy(columns=[branch])[branch]

        return self._build_structured_array(data)

    def _extract_object_collection(self, df, name, config, lengths, h5f):
        max_objects = config['max_objects']
        selection_branch = config.get("selection")

        # Ensure selection branch is included if it's used
        if selection_branch and selection_branch not in config['branches']:
            logging.debug(f"Adding selection branch {selection_branch} to branches for {name}")
            config['branches'].append(selection_branch)
    
        # Repeat data if this ObjectCollection is linked to a parent Object
        indices = None
        repeat_count = None
        if config.get('object_link'):
            link_object = config['object_link']['object']
            logging.debug(f"Duplicating data for {name} based on length of {link_object} Object per event.")
            repeat_count = lengths.get(link_object, [])
            logging.debug(f"Got {len(repeat_count)} lengths for vector object {link_object}")
            if repeat_count == []:
                logging.warning(f"Link object {link_object} not found in vector object lengths dictionary. This will result in a mismatch between the Objects and ObjectCollection lengths.")

            link_col = config['object_link']['link']
            raw_link_data = df.AsNumpy(columns=[link_col])[link_col]    
            # Flatten just one level (event -> jets), each item is a vector<int>
            obj_collection_indices = [jet for event in raw_link_data for jet in event]
            logging.debug(f"Extracted {len(obj_collection_indices)} link indices")
            # Convert ROOT RVec to numpy array
            indices = [r2h5.convert_rvec_to_numpy(collection_indices) for collection_indices in obj_collection_indices]
            logging.debug(f"Got {len(indices)} indices for {name} ObjectCollection")

        # Extract raw branch data
        selection_data = self._get_associated_object_collection_data(df, selection_branch, indices, repeat_count) if selection_branch else None
        saved_valid = False
        for branch in config['branches']:
            # Get the raw data
            raw_branch_data = self._get_associated_object_collection_data(df, branch, indices, repeat_count)
            
            # Apply selection if provided
            if selection_data:
                raw_branch_data = [
                    arr[mask.astype(bool)] for arr, mask in zip(raw_branch_data, selection_data)
                ]

            # Final padding
            data = {}
            padded, valid = r2h5.fix_array_size_and_create_valid(
                raw_branch_data, max_objects, compute_valid=("valid" not in config)
            )
            data[branch] = padded
            if valid is not None and not saved_valid:
                data["valid"] = valid
                saved_valid = True

            # Save the data to HDF5
            structured_data = self._build_structured_array(data)
            self._save_to_h5(h5f, name, structured_data)

    def _get_associated_object_collection_data(self, df, branch, indices, repeat_count):
        logging.info(f"Extracting branch {branch}")
        raw_branch_data =  [r2h5.convert_rvec_to_numpy(x) for x in df.AsNumpy(columns=[branch])[branch]]
        if indices and repeat_count:
            raw_branch_data = self._repeat_vectors(raw_branch_data, repeat_count)
            raw_branch_data = [raw_branch_data[i][idx.astype(np.int32)] for i, idx in enumerate(indices)]
        self._log_memory_snapshot()
        return raw_branch_data

    def _repeat_vectors(self, data_list, counts):
        repeated = []
        for i in range(len(counts)):
            repeated.extend([data_list[i]] * counts[i])
        return repeated

    def _build_structured_array(self, data_dict):
        dtype = [(k, v.dtype) for k, v in data_dict.items()]
        arrays = [data_dict[k] for k in data_dict]
        logging.debug(f"Building structured array with dtype {dtype} and data with shapes:")
        for k, v in data_dict.items():
            logging.debug(f"    {k}: {v.shape}")
        return np.core.records.fromarrays(arrays, dtype=dtype)

    def _save_to_h5(self, h5f, name, data):
        logging.debug(f"Saving {name} as a dataset.")

        # If the dataset already exists, extend it
        if name in h5f:
            logging.debug(f"Dataset {name} already exists. Extending it.")
            existing = h5f[name][:]
            old_dtype = existing.dtype
            new_dtype = old_dtype.descr.copy()

            # Add any new fields from incoming data
            for field in data.dtype.names:
                if field not in old_dtype.names:
                    new_dtype.append((field, data[field].dtype.str))
                    logging.debug(f"Appending new field '{field}' to dataset '{name}'")

            # Build extended structured array
            extended_data = np.empty(existing.shape, dtype=new_dtype)

            # Copy old data
            for field in old_dtype.names:
                extended_data[field] = existing[field]

            # Copy new fields (fill missing ones with default values)
            for field in extended_data.dtype.names:
                if field in data.dtype.names:
                    extended_data[field] = data[field]
                elif field not in old_dtype.names:
                    extended_data[field] = np.zeros(existing.shape, dtype=extended_data[field].dtype)

            del h5f[name]
            h5f.create_dataset(name, data=extended_data)

        else:
            h5f.create_dataset(name, data=data)

    def _start_memory_monitor(self):
        tracemalloc.start()
        current, peak = tracemalloc.get_traced_memory()
        logging.debug(f"Memory monitor started")
        self.memory_usage = [(datetime.now()-datetime.now(), current, peak)]

    def _log_memory_snapshot(self, tag=""):
        current, peak = tracemalloc.get_traced_memory()
        self.memory_usage.append((datetime.now()-self.memory_usage[0][0], current, peak))
        logging.debug(f"Current: {current / 1024 / 1024:.2f} MB; Peak: {peak / 1024 / 1024:.2f} MB")
    
    def _plot_memory_profile(self, file_index_offset=0):
        import matplotlib.pyplot as plt
        timestamps, current, peak = zip(*self.memory_usage)
        plt.plot(timestamps, current, label="Current Memory", color='red')
        plt.plot(timestamps, peak, label="Peak Memory", color='black')
        plt.xlabel("Time (s)")
        plt.ylabel("Memory (MB)")
        plt.legend()
        os.mkdir(os.path.join(self.output_path,"memlog"), exist_ok=True)
        plt.savefig(f"{self.output_path}/memlog_{file_index_offset:03}.png")
        plt.close()
        logging.debug(f"Memory profile saved to {self.output_path}/memlog_{file_index_offset:03}.png")