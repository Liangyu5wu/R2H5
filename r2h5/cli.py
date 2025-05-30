#!/usr/bin/env python

import argparse
import logging
from r2h5 import setup_logging
from r2h5.config_parser import load_yaml_config
from r2h5.converter import DatasetConverter

def main():
    parser = argparse.ArgumentParser(description="Convert ROOT TTrees to HDF5")
    parser.add_argument("--config", "-c", type=str, required=True, help="Path to YAML configuration file")
    parser.add_argument("--n-threads", "-t", type=int, default=1, help="Number of threads to use")
    parser.add_argument("--output-subfolder", '-o', type=str, default=None, help="Subfolder name to save output files on top of the paths specified in the config")
    parser.add_argument("--input-file", "-i", type=str, default=None, help="Since input ROOT file that overrides the config, which can be used for batch running")
    parser.add_argument("--max-events-per-file", "-m", type=int, default=None, help="Maximum number of events per output file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--batch", choices=["slurm", "condor"], help="Run in batch mode using the specified batch system")
    parser.add_argument("--file-index-offset", type=int, default=0, help="Offset for file index in batch mode")
    parser.add_argument("--dry-run", action="store_true", help="Dry run batch submission or deleting incomplete files")
    parser.add_argument("--overwrite-existing-output-files", "-k", action="store_true", help="Overwrite existing output files")
    parser.add_argument("--delete-incomplete-output-files", "-d", action="store_true", help="Delete incomplete files")
    parser.add_argument("--save-intermediate", "-s", action="store_true", help="Save intermediate ROOT files [CURRENTLY NOT IMPLEMENTED]")
    args = parser.parse_args()

    # Load configuration and run converter
    setup_logging(logging.DEBUG if args.debug else logging.INFO)
    config = load_yaml_config(
        config_path = args.config, 
        input_file = args.input_file,
        output_subfolder = args.output_subfolder
    )
    converter = DatasetConverter(config, save_intermediate=args.save_intermediate, overwrite_existing_output_files=args.overwrite_existing_output_files)
    if args.delete_incomplete_output_files:
        converter.delete_incomplete_output_files(dry_run=args.dry_run)
        return

    # Run interactively or in batch mode
    if args.batch:
        converter.submit_batch(args.config, args.batch, dry_run=args.dry_run, debug=args.debug)
    else:
        converter.format_ntuples(n_threads=args.n_threads, max_events_per_file=args.max_events_per_file)
        converter.run(file_index_offset=args.file_index_offset)

if __name__ == "__main__":
    main()