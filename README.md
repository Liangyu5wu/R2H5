# R2H5

This package serves as a flexible tool for converting TTree objects stored in ROOT files into ML-ready h5 datasets. 

Authors: Brendon Bullard (SLAC), Mirella Vassilev (Stanford/SLAC)

## First Time Setup

The package requirements are recommended to be setup with conda, and then the r2h5 package can be installed within the environment. For first-time installation, do the following:

```
conda env create -f environment.yaml
conda activate r2h5
pip install -e .
```

For future setups, one only needs to activate the `r2h5` conda environment. The package can be developed in-place thanks to the local pip installation using the `-e` flag.

## How to Run

Prepare a configuration YAML file defining the input files, tree name, output path, and data structure to extract. Then run:

```bash
r2h5 -c configs/<my_config>.yaml
```

Use `r2h5 --help` to view command-line options. To inspect the output:

```bash
python inspect_h5.py <my_output_file>.h5
```

## Output Datasets

Two primary types of data structures:

- `Object`: Used for per-object data (e.g., event-level scalars or vectorized objects).
- `ObjectCollection`: Used for collections associated with an object (e.g., tracks per jet).

These datasets are matched across the first dimension (event-wise or object-wise).

## Input Datasets

Input and output datasets are registered in the YAML configuration:
```
input:
  base_path: &base_path "/path/to/my/ntuples/"
  root_file: "my_path/files.*.root"
  tree_name: "ntuple"

output:
  base_path: *base_path
  h5_path: "output/folder/"
```

Base type conversion is determined on-the-fly to `numpy` accepted types. You will see an error message if the type conversion fails for any reason. This package supports two primary data handling modes:

### Case 1: `Object:scalar` and `ObjectCollection:vector`

Used when the base unit is the event, and you want to extract scalar features and vector collections per event. 

```
Objects:
  event:
    source_format: scalar
    branches:
      - Njets
      - generatorWeight
      ...

ObjectCollections:
  jets:
    source_format: vector
    branches:
      - jet_pt
      - jet_bTag_WP
      ...
    selection: jet_is_selected_boolean
    max_objects: 10

  muons:
    source_format: vector
    branches:
      - muon_pt
      - muon_WP
      ...
    selection: muon_is_selected_boolean
    max_objects: 2
  ...
```

### Case 2: `Object:vector` and `ObjectCollection:vector` with linking

Used when the base unit is an object (e.g., jet), and each object links to a collection (e.g., tracks, flow objects).

```
Objects:
  jets:
    source_format: vector
    branches:
      - AntiKt4EMTopoJets_pt
      - AntiKt4EMTopoJets_eta
      ...
    event_number: True # Saves the event number per-jet

ObjectCollections:
  tracks:
    source_format: vector
    branches:
      - Track_pt
      - Track_eta
      ...
    selection: Track_selection_boolean
    max_objects: 40
    object_link:
      object: jets
      link: AntiKt4EMTopoJets_btagTrack_idx
```
The branch `AntiKt4EMTopoJets_btagTrack_idx` is a `vector<vector<int>>` where the first dimension indexes over the jets and the second dimension indexes over the associated track indices.

## On-the-Fly Processing

You can define custom preprocessing functions in:

- `r2h5/cpp_helpers`: C++ functions for ROOT-level processing, get JIT compiled and available to RDF Define calls.
- `r2h5/rdf_defines`: PyROOT snippets or C++ defines registered before conversion.

Example definition in input config:

```yaml
cpp_helpers:
  - ftag_pileup.h
rdf_defines:
  - super_ntuples.ftag_pileup_trackVariables
  - super_ntuples.ftag_pileup_jetTruthVariables
```

## Batch Mode Execution

Use SLURM or HTCondor to parallelize conversion over many ROOT files:

```bash
r2h5 -c configs/<my_config>.yaml --batch slurm
```

Helpful flags:

- `--delete-incomplete-output-files`: Remove partially written `.h5` files.
- `--overwrite-existing-output-files`: Reprocess and overwrite any existing `.h5` files.

Example YAML file definitions for batch parameters for SLURM:
```
batch:
  batch_name: "r2h5_my_job"
  memory: 4 # GB
  time: 00:120:00 # 2 hour
  partition: roma
  account: atlas:usatlas
  max_files: -1
  cpu_count: 1
```

## Future Features

- HTCondor batch submission

For support, reach out to the maintainers or open an issue in the project repository.