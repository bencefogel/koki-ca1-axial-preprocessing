import numpy as np
import pandas as pd
import os


def save_in_chunks(current_values, output_dir, chunk_size=None):
    """
    Save the current_values array in chunks along the columns to the specified output directory.

    Parameters:
        current_values (numpy.ndarray): The array of numerical values to be saved.
        output_dir (str): The directory where the chunks will be saved.
        chunk_size (int): The number of columns to save per chunk (default is all columns).
    """
    os.makedirs(output_dir, exist_ok=True)

    # If no chunk_size is provided, save the whole array in one file
    if chunk_size is None:
        chunk_size = current_values.shape[1]

    num_chunks = current_values.shape[1] // chunk_size + (1 if current_values.shape[1] % chunk_size != 0 else 0)

    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, current_values.shape[1])

        chunk_values = current_values[:, start_idx:end_idx]

        chunk_file = os.path.join(output_dir, f"current_values_chunk_{i}.npy")

        np.save(chunk_file, chunk_values)
        print(f"Saved column chunk {i} to {chunk_file}")


def get_segment_iax(segment, df):
    """
    Returns a DataFrame containing the axial current values for a specific segment.

    This function extracts the axial currents associated with a
    specified segment. It handles both cases where the segment is a reference (ref)
    or a parent (par) in the provided MultiIndex DataFrame.

    Parameters:
        segment (str): The name of the segment whose axial currents are to be extracted.
        df (pd.DataFrame): A DataFrame with a MultiIndex containing 'ref' and 'par'
                           levels, and values representing axial currents.

    Returns:
        pd.DataFrame: A DataFrame containing the axial currents for the given segment.
    """
    ref_mask = df.index.get_level_values("ref") == segment
    ref_iax = -1 * df[ref_mask]  # negated, because axial currents are calculated from the perspective of the parent node

    par_mask = df.index.get_level_values("par") == segment
    par_iax = df[par_mask]

    df_iax_seg = pd.concat([ref_iax, par_iax], axis=0)

    return df_iax_seg
