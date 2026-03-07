import os
import re
import glob

import pandas as pd
import seaborn as sns

from config_loader import load_config
from plots.error_by_dow import ErrorByDOW
from plots.error_by_hour import ErrorByHour
from plots.error_dist import ErrorDist
from plots.timeseries import TimeSeriesPlotter
from plots.correlation_heatmap import CorrelationHeatmap

# Matches: consolidated_<n>_predictions.csv  ->  captures <n>
FILENAME_RE = re.compile(r"^consolidated_([a-zA-Z0-9_]+)_predictions\.csv$", re.IGNORECASE)


def parse_dataset_name(filename: str) -> tuple[str, str]:
    """
    Returns (pretty_name, slug) from a CSV filename.
      'consolidated_marconi100_predictions.csv' -> ('Marconi100', 'marconi100')
      'consolidated_my_cluster_predictions.csv' -> ('My Cluster', 'my_cluster')
    """
    match = FILENAME_RE.match(filename)
    if not match:
        raise ValueError(
            f"Filename '{filename}' doesn't match expected pattern: "
            "consolidated_<n>_predictions.csv"
        )
    slug        = match.group(1).lower()
    pretty_name = match.group(1).replace("_", " ").title()
    return pretty_name, slug


def discover_csvs(input_dir: str) -> list[str]:
    """Return sorted list of matching CSV paths found in input_dir."""
    pattern = os.path.join(input_dir, "consolidated_*_predictions.csv")
    paths = sorted(glob.glob(pattern))
    if not paths:
        raise FileNotFoundError(
            f"No files matching 'consolidated_*_predictions.csv' found in '{input_dir}'"
        )
    return paths


def run_pipeline(csv_path: str) -> None:
    """Run the full plotting pipeline for a single CSV file."""
    filename             = os.path.basename(csv_path)
    dataset_name, slug   = parse_dataset_name(filename)

    # Load defaults, deep-merged with any per-dataset overrides
    cfg = load_config(slug)

    output_path = os.path.join(cfg["paths"]["output_dir"], slug)
    os.makedirs(output_path, exist_ok=True)

    print(f"┌─ Dataset : {dataset_name}  (config: defaults + {slug}.toml if present)")
    print(f"│  Source  : {csv_path}")
    print(f"│  Output  : {output_path}/")

    df = pd.read_csv(csv_path)
    df[cfg["columns"]["date"]] = pd.to_datetime(df[cfg["columns"]["date"]])
    sns.set_style(cfg["plot"]["style"])

    # Each entry: (plotter_key, constructor)
    # Skipped automatically if plotters.<key>.enabled = false in config
    plotters = [
        ("timeseries",          lambda: TimeSeriesPlotter(df, dataset_name, output_path, cfg).plot()),
        ("error_by_hour",       lambda: ErrorByHour(df, dataset_name, output_path, cfg).plot()),
        ("error_dist",          lambda: ErrorDist(df, dataset_name, output_path, cfg).plot()),
        ("error_by_dow",        lambda: ErrorByDOW(df, dataset_name, output_path, cfg).plot()),
        ("correlation_heatmap", lambda: CorrelationHeatmap(df, dataset_name, output_path, cfg).plot()),
    ]

    for key, plotter_fn in plotters:
        if not cfg["plotters"][key].get("enabled", True):
            print(f"│  Skipping {key} (disabled in config)")
            continue
        print(f"│  Plotting {key}...")
        plotter_fn()

    print(f"└─ Done.\n")


if __name__ == "__main__":
    # Input dir comes from defaults.toml [paths] but can be overridden here
    defaults = load_config()
    csv_files = discover_csvs(defaults["paths"]["input_dir"])
    print(f"Found {len(csv_files)} dataset(s) in '{defaults['paths']['input_dir']}'\n")
    for path in csv_files:
        run_pipeline(path)
