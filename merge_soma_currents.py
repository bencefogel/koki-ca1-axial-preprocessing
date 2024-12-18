import os
import pandas as pd
import numpy as np
from utils import get_segment_iax

# Input and output directories
input_dir = 'L:/cluster_seed30/preprocessed_data/axial_currents'
output_dir = 'L:/cluster_seed30/preprocessed_data/axial_currents_merged_soma'

# Load the index
index = pd.read_csv(os.path.join(input_dir, 'multiindex.csv'))

# Ensure the index is saved only once
index_saved = False


def merge_soma_segments(index, values):
    """
    Processes and merges soma-related axial currents in the dataset.

    Parameters:
        index (df): The multiindex DataFrame containing 'ref' and 'par' columns.
        values (np.ndarray): The array of axial current values corresponding to the multiindex.

    Returns:
        df_iax_updated (df): A DataFrame with soma axial currents updated and other segments preserved.
    """
    # Create a DataFrame with a MultiIndex
    multiindex = pd.MultiIndex.from_frame(index)
    df = pd.DataFrame(data=values, index=multiindex)

    # Get axial currents for specific soma segments
    df_iax_soma_1 = get_segment_iax('soma(0.166667)', df)
    df_iax_soma_2 = get_segment_iax('soma(0.5)', df)
    df_iax_soma_3 = get_segment_iax('soma(0.833333)', df)
    df_iax_soma_4 = get_segment_iax('soma(1)', df)

    # Soma-dendrite axial currents
    iax_dend1 = df_iax_soma_4.loc[[("dend1_0(0.5)", "soma(1)")]]
    iax_dend2 = df_iax_soma_3.loc[[("dend2_0(0.5)", "soma(0.833333)")]]
    iax_dend3 = df_iax_soma_2.loc[[("dend3_0(0.5)", "soma(0.5)")]]
    iax_dend4 = df_iax_soma_4.loc[[("dend4_0(0.166667)", "soma(1)")]]
    iax_dend5 = df_iax_soma_4.loc[[("dend5_0(0.166667)", "soma(1)")]]
    iax_hill = df_iax_soma_2.loc[[("hill(0.166667)", "soma(0.5)")]]

    # Merge soma axial currents
    df_iax_soma_merged = pd.concat((iax_dend1, iax_dend2, iax_dend3, iax_dend4, iax_dend5, iax_hill), axis=0)

    # Update parent labels to 'soma'
    index_tuples = df_iax_soma_merged.index.tolist()
    new_index_tuples = [(ref, 'soma') for ref, par in index_tuples]
    new_index = pd.MultiIndex.from_tuples(new_index_tuples, names=df_iax_soma_merged.index.names)
    df_iax_soma_merged.index = new_index

    # Remove internal axial current rows (with "soma" in "ref")
    ref_idx = df[df.index.get_level_values("ref").str.contains("soma")].index
    df_iax_ref_removed = df.drop(ref_idx)

    # Remove original soma-dendrite axial currents (with "soma" in "par")
    par_idx = df_iax_ref_removed[df_iax_ref_removed.index.get_level_values("par").str.contains("soma")].index
    df_iax_removed = df_iax_ref_removed.drop(par_idx)

    # Combine updated segments
    df_iax_updated = pd.concat([df_iax_removed, df_iax_soma_merged], axis=0)
    return df_iax_updated


def process_all_files(index, input_dir, output_dir):
    """
    Processes all axial current chunks in the directory and saves the results.

    This function loops through all files in the specified directory that match the naming
    convention `current_values_chunk_*.npy`, processes them to update soma axial currents,
    and saves the resulting values and index.

    Parameters:
        index (df): The multiindex DataFrame containing 'ref' and 'par' columns.
        input_dir (str): The directory containing `multiindex.csv` and the `.npy` value chunks.
        output_dir (str): The directory where the processed files will be saved.

    Returns:
        None: Saves the processed chunks and the merged index to the output directory.
    """
    global index_saved

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Loop through all chunk files in the input directory
    for chunk_file in sorted(os.listdir(input_dir)):
        if chunk_file.startswith('current_values_chunk_') and chunk_file.endswith('.npy'):
            chunk_path = os.path.join(input_dir, chunk_file)

            # Load the current values chunk
            values = np.load(chunk_path)

            # Merge soma segments
            df_iax_updated = merge_soma_segments(index, values)

            # Save the updated values chunk
            chunk_number = chunk_file.split('_')[-1].split('.')[0]  # Extract chunk number
            chunk_output_file = os.path.join(output_dir, f'merged_soma_values_{chunk_number}.npy')
            np.save(chunk_output_file, df_iax_updated.values)

            # Save the index only once
            if not index_saved:
                index_output_file = os.path.join(output_dir, 'multiindex_merged_soma.csv')
                df_iax_updated.index.to_frame().reset_index(drop=True).to_csv(index_output_file, index=False)
                index_saved = True


# Process all axial current chunks
process_all_files(index, input_dir, output_dir)
