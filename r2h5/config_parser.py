import yaml
import os, glob

def load_yaml_config(config_path, input_file=None, output_subfolder=None):
    """Load YAML configuration file."""
    with open(config_path, "r") as f:
        raw_config = yaml.safe_load(f)
        # parse list of input files and prepare full output path
        config = format_paths(raw_config, input_file, output_subfolder)
        config = add_internal_settings(config)
        return config 

def format_paths(config, input_file, output_subfolder):
    """Glob multiple files."""

    # Replace input file with single path if provided
    if input_file:
        config["input"]["root_file_list"] = [input_file]
    else:
        config["input"]["root_file_list"] = glob.glob(os.path.join(
            config["input"].get("base_path",""), config["input"]["root_file"]
        ))
    config['input'].pop('root_file')

    config["output"]["h5_path"] = os.path.join(
        config["output"].get("base_path",""), 
        config["output"]["h5_path"],
        output_subfolder if output_subfolder else ""
    )
 
    return config

def add_internal_settings(config):
    for obj, obj_config in config["Objects"].items():
        # Add internal settings to each object
        for objcol, objcol_config in config["ObjectCollections"].items():
            if "object_link" in objcol_config and objcol_config["object_link"]["object"] == obj:
                obj_config["store_length"] = True
    return config