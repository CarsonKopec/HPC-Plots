import matplotlib.pyplot as plt
import seaborn as sns
from pandas import DataFrame


class ErrorDist:
    def __init__(self, df: DataFrame, dataset_name: str, output_path: str, cfg: dict):
        self.df = df
        self.dataset_name = dataset_name
        self.output_path = output_path
        self.cfg = cfg

    def plot(self):
        plot  = self.cfg["plot"]
        pcfg  = self.cfg["plotters"]["error_dist"]
        error = self.cfg["columns"]["error"]   # {"LGBM": col, "SVR": col}

        fig, ax = plt.subplots(figsize=plot["figsize"]["medium"])

        for label, col in error.items():
            sns.kdeplot(data=self.df, x=col, label=label, fill=True, alpha=0.4, ax=ax)

        ax.axvline(0, linestyle="--", linewidth=1)

        # Annotate peaks
        for collection, label in zip(ax.collections, error.keys()):
            verts   = collection.get_paths()[0].vertices
            peak_i  = verts[:, 1].argmax()
            ax.annotate(
                label,
                xy=(verts[peak_i, 0], verts[peak_i, 1]),
                xytext=(0, 10),
                textcoords="offset points",
                ha="center",
                fontsize=11,
                fontweight="bold",
                color=collection.get_facecolor()[0],
            )

        ax.set_title(f"Prediction Error Distribution ({self.dataset_name})")
        ax.set_xlabel("Signed Error (kWh)")
        ax.legend().remove()
        plt.tight_layout()
        plt.savefig(f"{self.output_path}/{pcfg['filename']}", dpi=plot["dpi"])
        plt.close(fig)
