"""
config_loader.py
────────────────
Loads a two-level TOML config:
  1. config/defaults.toml        — shared settings for all datasets
  2. config/<dataset_slug>.toml  — optional per-dataset overrides (deep-merged)

Usage:
    from config_loader import load_config
    cfg = load_config("marconi100")   # slug = lowercase, underscored dataset name
    cfg = load_config()               # defaults only
"""

import tomllib
from pathlib import Path
from copy import deepcopy
from typing import Any

CONFIG_DIR = Path(__file__).parent / "config"
DEFAULTS_PATH = CONFIG_DIR / "defaults.toml"


def _deep_merge(base: dict, override: dict) -> dict:
    """
    Recursively merge `override` into a deep copy of `base`.
    Nested dicts are merged; all other values are replaced.
    """
    result = deepcopy(base)
    for key, val in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = deepcopy(val)
    return result


def load_config(dataset_slug: str | None = None) -> dict[str, Any]:
    """
    Load and return the merged config for a given dataset slug.

    Args:
        dataset_slug: lowercase, underscore-separated name derived from the
                      CSV filename, e.g. "marconi100" or "supercloud".
                      If None or no matching file exists, returns defaults only.

    Returns:
        Merged config dict.
    """
    with open(DEFAULTS_PATH, "rb") as f:
        cfg = tomllib.load(f)

    if dataset_slug:
        override_path = CONFIG_DIR / f"{dataset_slug}.toml"
        if override_path.exists():
            with open(override_path, "rb") as f:
                overrides = tomllib.load(f)
            cfg = _deep_merge(cfg, overrides)

    return cfg
