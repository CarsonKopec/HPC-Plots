import numpy as np
from pandas import DataFrame


def smape(actual: np.ndarray, predicted: np.ndarray) -> float:
    """
    Symmetric Mean Absolute Percentage Error.
    Returns a percentage value (0–200).
    Rows where both actual and predicted are zero are excluded.
    """
    actual      = np.asarray(actual, dtype=float)
    predicted   = np.asarray(predicted, dtype=float)
    denominator = (np.abs(actual) + np.abs(predicted)) / 2
    mask        = denominator != 0
    return float(100 * np.mean(np.abs(actual[mask] - predicted[mask]) / denominator[mask]))


def wmape(actual: np.ndarray, predicted: np.ndarray) -> float:
    """
    Weighted Mean Absolute Percentage Error.
    Returns a percentage value (0–100+).
    Raises if sum of actuals is zero.
    """
    actual       = np.asarray(actual, dtype=float)
    predicted    = np.asarray(predicted, dtype=float)
    total_actual = np.sum(np.abs(actual))
    if total_actual == 0:
        raise ValueError("wMAPE is undefined when the sum of actuals is zero.")
    return float(100 * np.sum(np.abs(actual - predicted)) / total_actual)


def compute_metrics(df: DataFrame, dataset_name: str, cfg: dict) -> list[dict]:
    """
    Compute sMAPE and wMAPE for every model in cfg[columns][models].

    Args:
        df:           The loaded dataset DataFrame.
        dataset_name: Pretty name used as a label (e.g. "Marconi100").
        cfg:          Merged config dict from config_loader.

    Returns:
        List of dicts, one per model:
            [{"dataset": ..., "model": ..., "smape": ..., "wmape": ...}, ...]
    """
    actual_col = cfg["columns"]["actual_energy"]
    models     = cfg["columns"]["models"]
    actual     = df[actual_col].to_numpy()
    rows       = []

    print(f"│  Metrics for {dataset_name}:")

    for label, pred_col in models.items():
        if pred_col not in df.columns:
            print(f"│    [{label}] Column '{pred_col}' not found — skipping.")
            continue

        predicted = df[pred_col].to_numpy()
        s = smape(actual, predicted)
        w = wmape(actual, predicted)

        print(f"│    {label:<6}  sMAPE = {s:6.2f}%   wMAPE = {w:6.2f}%")
        rows.append({
            "dataset": dataset_name,
            "model":   label,
            "smape":   round(s, 4),
            "wmape":   round(w, 4),
        })

    return rows