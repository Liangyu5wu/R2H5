import h5py
import json
import sys

def format_dtype(dtype):
    """
    Format the dtype information nicely in columns.
    """
    # Check if the dtype is compound (i.e., has fields)
    if dtype.fields is not None:
        # Initialize an empty list to hold formatted string lines
        lines = []
        # Iterate over all fields in the dtype
        for field_name, (field_dtype, _) in dtype.fields.items():
            # Format each line with field name and its dtype
            line = f"{field_name:20s} : {field_dtype}"
            lines.append(line)
        # Join all lines into a single string
        formatted_dtype = "\n".join(lines)
    else:
        # For simple dtypes, just convert dtype to string
        formatted_dtype = str(dtype)
    
    return formatted_dtype

if len(sys.argv) != 2:
    print("Usage: python inspect_h5.py my_file.h5")
else:
    # Open the h5 file for reading
    h5_file = h5py.File(sys.argv[1], 'r')
    
    # Iterate over all keys in the file
    for key in h5_file.keys():
        print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(f"~~~~~~ Key: [{key}] (size {len(h5_file[key])}) ~~~~~~~~")
        # Use the format_dtype function to print dtype info nicely
        print(format_dtype(h5_file[key].dtype))
    
    # Don't forget to close the file when done
    h5_file.close()

