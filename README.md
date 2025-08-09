# R2H5

This package serves as a flexible tool for converting TTree objects stored in ROOT files into ML-ready h5 datasets. 

Authors: Brendon Bullard (SLAC), Mirella Vassilev (Stanford/SLAC)

## First Time Setup

### Method 1: Using UV (Recommended)

The package can be easily set up using UV, a fast Python package installer and resolver.

**Prerequisites:**
- ROOT framework must be installed separately (see ROOT Installation section below)

**Installation:**
```bash
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv --python 3.9
source .venv/bin/activate
uv pip install -r requirements.txt

# Install r2h5 package in development mode
uv pip install -e .
```

**Or use the automated setup script:**
```bash
chmod +x setup.sh
./setup.sh
```

### Method 2: Using Conda (Alternative)

For users who prefer conda or have issues with ROOT installation:

```bash
conda env create -f environment.yaml
conda activate r2h5
pip install -e .
```

### ROOT Installation

ROOT framework is required but not automatically installed. Choose one method:

**Option 1: Conda (Easiest)**
```bash
conda install -c conda-forge root
```

**Option 2: System Package Manager**
```bash
# Ubuntu/Debian
sudo apt-get install root-system

# CentOS/RHEL
sudo yum install root
```

**Option 3: From Source**
Follow instructions at: https://root.cern/install/build_from_source/

## Activation for Future Use

**For UV setup:**
```bash
source .venv/bin/activate
```

**For Conda setup:**
```bash
conda activate r2h5
```

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
```yaml
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

```yaml
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

```yaml
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
```yaml
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
