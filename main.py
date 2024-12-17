import numpy as np
import pandas as pd
import os

from tqdm import tqdm
from utils import save_in_chunks

input_dir = 'L:/cluster_seed30/raw_data/'
v = np.load(input_dir+'/membrane_potential_data/v.npy').astype(np.float32)
segments = np.load(input_dir+'/membrane_potential_data/segments.npy')

df_v = pd.DataFrame(data=v)
df_v.insert(0, 'segment', segments)
df_connections = pd.read_csv(input_dir+'df_connections.csv', index_col=0)

iax = np.empty((df_connections.shape[0], df_v.shape[1]-1))

for i in tqdm(range(len(df_connections.iloc[:, 0]))):
    try:
        ref = df_connections.iloc[i, 0]
        par = df_connections.iloc[i, 1]
        ri_par = df_connections.iloc[i, 2]

        v_ref = df_v[df_v['segment'] == ref].iloc[0, 1:].values
        v_par = df_v[df_v['segment'] == par].iloc[0, 1:].values

        iax_row = (v_par - v_ref) / ri_par
    except IndexError:
        print(f"The following segment does not have a parent: {df_connections.iloc[i,0]}")
        iax_row = np.zeros(df_v.shape[1]-1)

    iax[i, :] = iax_row

index_df = pd.DataFrame(data={'ref': df_connections['ref'].values, 'par': df_connections['par'].values})
output_dir = 'L:/cluster_seed30/preprocessed_data/axial_currents'
os.makedirs(output_dir, exist_ok=True)
index_file = os.path.join(output_dir, "multiindex.csv")
index_df.to_csv(index_file, index=False)

save_in_chunks(iax, output_dir, chunk_size=20000)
