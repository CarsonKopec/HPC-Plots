"""
metrics_summary.py
──────────────────
Receives the consolidated metrics DataFrame built up in main.py,
writes metrics.csv, and renders a grouped bar chart summary as
metrics_summary.png in the base output directory.

Called automatically from main.py after all datasets are processed.
Can also be run standalone (reads existing metrics.csv):
    python metrics_summary.py
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def build_summary(df: pd.DataFrame, output_dir: str, dpi: int = 150) -> None:
    """
    Write consolidated metrics.csv and render the summary bar chart.

    Args:
        df:         Consolidated metrics DataFrame with columns:
                    dataset, model, smape, wmape.
        output_dir: Base output directory (e.g. "plots/").
        dpi:        Output image resolution.
    """
    os.makedirs(output_dir, exist_ok=True)

    # ── Write consolidated CSV ─────────────────────────────────────────────────
    csv_path = os.path.join(output_dir, "metrics.csv")
    df.to_csv(csv_path, index=False)
    print(f"│  Saved metrics  → {csv_path}")

    # ── Bar chart ──────────────────────────────────────────────────────────────
    models   = df["model"].unique().tolist()
    datasets = df["dataset"].unique().tolist()

    palette = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    colours = {ds: palette[i % len(palette)] for i, ds in enumerate(datasets)}

    x     = np.arange(len(models))
    n_ds  = len(datasets)
    width = 0.7 / n_ds

    fig, axes = plt.subplots(2, 1, figsize=(max(8, 2.5 * len(models)), 9), sharex=True)
    fig.suptitle("Model Error Metrics — All Datasets", fontsize=14, fontweight="bold", y=0.98)

    for ax, metric, title, ylabel in [
        (axes[0], "smape", "sMAPE (%)", "sMAPE (%)"),
        (axes[1], "wmape", "wMAPE (%)", "wMAPE (%)"),
    ]:
        for i, ds in enumerate(datasets):
            subset = df[df["dataset"] == ds].set_index("model")
            values = [subset.loc[m, metric] if m in subset.index else float("nan")
                      for m in models]
            offset = (i - n_ds / 2 + 0.5) * width
            bars   = ax.bar(x + offset, values, width=width,
                            label=ds, color=colours[ds], edgecolor="white", linewidth=0.5)

            for bar, val in zip(bars, values):
                if not np.isnan(val):
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 0.1,
                        f"{val:.2f}",
                        ha="center", va="bottom", fontsize=8, fontweight="bold",
                    )

        ax.set_title(title, fontsize=12, fontweight="bold", pad=8)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels(models, fontsize=11)
        ax.set_ylim(0, ax.get_ylim()[1] * 1.18)
        ax.axhline(0, color="grey", linewidth=0.5)
        ax.legend(title="Dataset", fontsize=9, title_fontsize=9,
                  loc="upper right", framealpha=0.8)
        sns.despine(ax=ax)

    axes[1].set_xlabel("Model", fontsize=11)
    plt.tight_layout()

    img_path = os.path.join(output_dir, "metrics_summary.png")
    plt.savefig(img_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"│  Saved summary  → {img_path}")


# ── Standalone entry point ─────────────────────────────────────────────────────
if __name__ == "__main__":
    from config_loader import load_config
    cfg      = load_config()
    csv_path = os.path.join(cfg["paths"]["output_dir"], "metrics.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"No consolidated metrics.csv found at '{csv_path}'. "
            "Run main.py first to generate it."
        )

    df = pd.read_csv(csv_path)
    build_summary(df, cfg["paths"]["output_dir"], dpi=cfg["plot"]["dpi"])