import numpy as np
import logging

def get_dtype(rvec):
    """Determine the dtype for numpy array based on the type of elements in RVec."""
    try:
        if len(rvec) > 0:
            if isinstance(rvec[0], float):
                return np.float64
            elif isinstance(rvec[0], int):
                return np.int32
            elif isinstance(rvec[0], str):
                return np.int8
            elif isinstance(rvec[0], bool):
                return np.bool_
            else:
                logging.warning(f"Unknown type {type(rvec[0])} in RVec, using default dtype np.float32")
    except OverflowError:
        logging.error("OverflowError: RVec too large to evaluate length.")
    except Exception as e:
        logging.error(f"Unexpected error when determining dtype: {e}")
    return np.float32

def convert_rvec_to_numpy(rvec):
    """Convert ROOT RVec to a numpy array with appropriate dtype."""
    dtype = get_dtype(rvec)
    try:
        if dtype == np.int8:
            def char_to_int8(c):
                val = ord(c)
                return val if val < 128 else val - 256  # 2's complement for 8-bit
            return np.array([char_to_int8(rvec[i]) for i in range(len(rvec))], dtype=np.int8)
        return np.array(rvec, dtype=dtype)
    except TypeError as e:
        logging.error(f"TypeError: {e} converting {type(rvec[0])} to {dtype}.")
        logging.error(f"type(rvec): {type(rvec)}")
        logging.error(f"rvec[0]: {repr(rvec[0])}")
        exit(1)

def fix_array_size(arrays, max_size):
    """Ensure all arrays are of the maximum specified size, pad with NaN where necessary."""
    if len(arrays) == 0:
        return np.array([], dtype=np.float32)  # Empty array if no data is present
    dtype = arrays[0].dtype
    return np.array([np.pad(a, (0, max_size - len(a)), mode='constant', constant_values=0) if len(a) < max_size else a[:max_size] for a in arrays], dtype=dtype)


def fix_array_size_and_create_valid(arrays, max_size, selection_key=None, compute_valid=True): # TODO implement selection_key
    """Ensure all arrays are of the maximum specified size, and optionally return a valid mask."""
    if not arrays:  # Check if arrays list is empty
        return np.array([], dtype=np.float32), np.array([], dtype=bool)

    dtype = arrays[0].dtype  # Assumes all arrays have the same dtype; adjust as necessary
    padded_arrays = []
    valid_masks = []

    for array in arrays:
        current_length = len(array)
        if current_length < max_size:
            # Pad the array and create a valid mask for this array
            padded_array = np.pad(array, (0, max_size - current_length), mode='constant', constant_values=0)
            valid_mask = np.zeros(max_size, dtype=bool)
            valid_mask[:current_length] = True
        else:
            padded_array = array[:max_size]
            valid_mask = np.ones(max_size, dtype=bool)

        padded_arrays.append(padded_array)
        valid_masks.append(valid_mask)

    # Convert lists to NumPy arrays
    padded_arrays_np = np.stack(padded_arrays)  # Use np.stack to ensure uniform dimensions
    if compute_valid: valid_masks_np = np.stack(valid_masks)
    else: valid_masks_np = None

    return padded_arrays_np, valid_masks_np

# Chad suggestion
# def fix_array_size_and_create_valid(arrays_dict, max_size, selection_key=None, compute_valid=True):
#     """
#     - arrays_dict: dict of {branch: List[np.array]} for each event.
#     - selection_key: name of the selection feature (must be a key in arrays_dict) or None.
#     """
#     if not arrays_dict:
#         return {}, None

#     n_events = len(next(iter(arrays_dict.values())))  # Number of events
#     padded_output = {key: [] for key in arrays_dict if key != selection_key}
#     valid_masks = []

#     for i in range(n_events):
#         # Selection mask for this event
#         if selection_key is not None:
#             selection_mask = arrays_dict[selection_key][i].astype(bool)
#         else:
#             selection_mask = np.ones_like(next(iter(arrays_dict.values()))[i], dtype=bool)

#         # Apply selection and pad each branch
#         valid_count = np.count_nonzero(selection_mask)
#         valid_count = min(valid_count, max_size)

#         if compute_valid:
#             valid_mask = np.zeros(max_size, dtype=bool)
#             valid_mask[:valid_count] = True
#             valid_masks.append(valid_mask)

#         for key, data_per_event in arrays_dict.items():
#             if key == selection_key:
#                 continue  # Skip writing the selection variable to output
#             selected = data_per_event[i][selection_mask]
#             padded = np.zeros(max_size, dtype=selected.dtype)
#             padded[:valid_count] = selected[:max_size]
#             padded_output[key].append(padded)

#     # Convert lists to numpy arrays
#     for key in padded_output:
#         padded_output[key] = np.stack(padded_output[key])
#     if compute_valid:
#         valid_masks_np = np.stack(valid_masks)
#         padded_output["valid"] = valid_masks_np

#     return padded_output
