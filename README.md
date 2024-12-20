# Axial current preprocessing
Code for calculating and preprocessing axial currents between segments of a CA1 pyramidal neuron model.

## **Configuration and Parameters**
### `main.py`
To calculate the axial currents, configure the following parameters:
1. **Input Directory (`input_dir`)**: Specify the path to the raw data files containing membrane potential and segment data. Example:
   ```python
   input_dir = 'L:/cluster_seed30/raw_data/'
   ```
2. **Output Directory (`output_dir`)**: Specify where the preprocessed axial current data will be saved. Example:
   ```python
   output_dir = 'L:/cluster_seed30/preprocessed_data/axial_currents'
   ```
3. **Chunk Size (`chunk_size`)**: Define the number of columns per chunk when saving the processed axial current data. Example:
   ```python
   chunk_size = 20000
   ```
### `merge_soma_currents.py`
To preprocess the axial currents by merging somatic segments, configure the following parameters:
1. **Input Directory (`input_dir`)**: Path to the preprocessed axial current data (from `main.py`). Example:
   ```python
   input_dir = 'L:/cluster_seed30/preprocessed_data/axial_currents'
   ```
2. **Output Directory (`output_dir`)**: Path where the merged somatic axial current data will be saved. Example:
   ```python
   output_dir = 'L:/cluster_seed30/preprocessed_data/axial_currents_merged_soma'
   ```

## **Performance**
- Execution time:
  - `main.py`: 5 minutes (to process ~1400 segment pairs and save the resulting data in chunks of 20k columns)
  - `merge_soma_currents.py`: 1 minute (for 11 files, each containing dataframes of dimensions ~1400 x 20k)

## **Workflow**
### 1. Calculate Axial Currents (`main.py`)
This script processes the input membrane potential data and calculates axial currents between connected segments.

#### Key Steps:
1. Load membrane potential and segment connection data.
2. Compute axial currents using the formula:
   ```
   I_axial = (V_parent - V_reference) / R_axial
   ```
   where `V_reference` and `V_parent` are membrane potentials for the connected segments, and `R_axial` is the axial resistance between them.
3. Save the axial current data in chunks for efficient storage and access.

### 2. Merge Soma Segments (`merge_soma_currents.py`)
This script merges multiple somatic segments into a single segment and updates the axial currents accordingly.

#### Key Steps:
1. Load the multiindex data and axial current chunks.
2. Identify and extract axial currents for all somatic segments.
3. Reconnect axial currents from soma-dendrite connections to a single somatic segment.
4. Remove original internal axial currents related to the soma and replace them with the merged soma segment data.
5. Save the updated axial current data and the new multiindex file.