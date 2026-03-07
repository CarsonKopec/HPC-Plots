# HPC Energy Prediction — Plot Pipeline

A reusable, config-driven pipeline for visualising HPC energy prediction errors across multiple datasets. Drop in a CSV, run one command, get a full set of plots.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
  - [defaults.toml](#defaultstoml)
  - [Per-dataset overrides](#per-dataset-overrides)
- [Usage](#usage)
- [Adding a New Dataset](#adding-a-new-dataset)
- [Plotters](#plotters)
- [Column Mappings](#column-mappings)

---

## Project Structure

```
├── main.py                        # Entry point
├── config_loader.py               # TOML loader with deep-merge
├── environment.yml                # Conda environment
│
├── config/
│   ├── defaults.toml              # Shared settings for all datasets
│   └── <dataset_slug>.toml        # Optional per-dataset overrides
│
├── data/                          # Input CSVs (one per dataset)
│   └── consolidated_<n>_predictions.csv
│
├── plots/                         # Output (auto-created)
│   └── <dataset_slug>/
│       ├── timeseries.png
│       ├── error_by_hour.png
│       ├── error_distribution.png
│       ├── error_by_dow.png
│       └── correlation_heatmap.png
│
├── timeseries.py
├── error_by_hour.py
├── error_dist.py
├── error_by_dow.py
└── correlation_heatmap.py
```

---

## Requirements

- [Conda](https://docs.conda.io/en/latest/miniconda.html) (Miniconda or Anaconda)
- Python 3.11+

All Python dependencies are declared in `environment.yml`.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/CarsonKopec/HPC-Plots
cd HPC-Plots
```

### 2. Create the Conda environment

```bash
conda env create -f environment.yml
```

This creates an environment named `hpc-plots` with all required dependencies.

### 3. Activate the environment

```bash
conda activate hpc-plots
```

### 4. Verify

```bash
python -c "import pandas, seaborn, matplotlib; print('OK')"
```

### Updating the environment

If `environment.yml` changes (e.g. a new dependency is added):

```bash
conda env update -f environment.yml --prune
```

### Removing the environment

```bash
conda deactivate
conda env remove -n hpc-plots
```

---

## Configuration

All settings live in TOML files inside the `config/` directory. The pipeline uses a two-level config system:

1. **`config/defaults.toml`** — shared settings applied to every dataset
2. **`config/<dataset_slug>.toml`** — optional per-dataset overrides (deep-merged on top of defaults)

Only specify what differs in a per-dataset file — everything else is inherited automatically.

### defaults.toml

```toml
[paths]
input_dir  = "data"
output_dir = "plots"

[plot]
dpi           = 150
style         = "darkgrid"
color_palette = "tab10"

[plot.figsize]
small  = [7, 5]
medium = [10, 5]
large  = [12, 6]

[plotters.timeseries]
enabled  = true
filename = "timeseries.png"

# ... (one block per plotter)

[columns]
date          = "start_date"
actual_energy = "real_energy_kwhr"

[columns.models]
LGBM = "predicted_energy_kwhr_LGBM"
SVR  = "predicted_energy_kwhr_SVR"

[columns.error]
LGBM = "signed_diff_energy_kwhr_LGBM"
SVR  = "signed_diff_energy_kwhr_SVR"

[columns.features]
list = ["user_diversity", "queued_jobs", "cores_used", ...]
```

### Per-dataset overrides

Create `config/<dataset_slug>.toml` where the slug is the lowercase, underscored name parsed from the CSV filename. For example, `consolidated_leonardo_predictions.csv` → `config/leonardo.toml`.

```toml
# config/leonardo.toml — only override what differs

[plot]
dpi = 300

[plotters.error_dist]
enabled = false   # skip this plot for Leonardo

[columns.error]
LGBM = "diff_energy_LGBM"   # different column name in this dataset
SVR  = "diff_energy_SVR"
```

---

## Usage

### 1. Place your CSVs in the `data/` folder

Files must follow the naming convention:

```
consolidated_<n>_predictions.csv
```

Examples: `consolidated_marconi100_predictions.csv`, `consolidated_leonardo_predictions.csv`

### 2. Run the pipeline

```bash
conda activate hpc-plots
python main.py
```

The script will:

1. Scan `data/` for all matching CSVs
2. Parse the dataset name from each filename using regex
3. Load `config/defaults.toml` merged with `config/<slug>.toml` (if it exists)
4. Run all enabled plotters for each dataset
5. Save plots to `plots/<slug>/`

**Example output:**

```
Found 2 dataset(s) in 'data'

┌─ Dataset : Marconi100  (config: defaults + marconi100.toml if present)
│  Source  : data/consolidated_marconi100_predictions.csv
│  Output  : plots/marconi100/
│  Plotting timeseries...
│  Plotting error_by_hour...
│  Plotting error_distribution...
│  Plotting error_by_dow...
│  Plotting correlation_heatmap...
└─ Done.

┌─ Dataset : Leonardo  (config: defaults + leonardo.toml if present)
│  Source  : data/consolidated_leonardo_predictions.csv
│  Output  : plots/leonardo/
│  Plotting timeseries...
│  Skipping error_dist (disabled in config)
...
└─ Done.
```

### Disable `__pycache__`

```bash
PYTHONDONTWRITEBYTECODE=1 python main.py
```

Or add to your shell profile to make it permanent:

```bash
export PYTHONDONTWRITEBYTECODE=1
```

---

## Adding a New Dataset

1. Drop `consolidated_<n>_predictions.csv` into `data/`
2. *(Optional)* Create `config/<n>.toml` with any overrides
3. Run `python main.py` — no code changes required

If your new dataset has different column names, add a `[columns]` override in its TOML file:

```toml
[columns.error]
LGBM = "my_custom_lgbm_error_col"
SVR  = "my_custom_svr_error_col"
```

---

## Plotters

| Key | Output file | Description |
|---|---|---|
| `timeseries` | `timeseries.png` | Actual vs predicted energy over time |
| `error_by_hour` | `error_by_hour.png` | Mean signed error per hour of day |
| `error_dist` | `error_distribution.png` | KDE of signed error distribution |
| `error_by_dow` | `error_by_dow.png` | Boxplot of signed error by day of week |
| `correlation_heatmap` | `correlation_heatmap.png` | Feature correlation matrix |

Each plotter can be enabled or disabled independently per dataset via its `[plotters.<key>]` block in the TOML config.

---

## Column Mappings

The pipeline is model-agnostic. Models are defined as key-value pairs in `[columns.models]` and `[columns.error]` — adding a third model requires only a config change:

```toml
[columns.models]
LGBM = "predicted_energy_kwhr_LGBM"
SVR  = "predicted_energy_kwhr_SVR"
XGB  = "predicted_energy_kwhr_XGB"   # new model — automatically appears in all plots

[columns.error]
LGBM = "signed_diff_energy_kwhr_LGBM"
SVR  = "signed_diff_energy_kwhr_SVR"
XGB  = "signed_diff_energy_kwhr_XGB"
```
