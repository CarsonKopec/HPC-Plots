import matplotlib.pyplot as plt
import seaborn as sns
from pandas import DataFrame


class CorrelationHeatmap:
    def __init__(self, df: DataFrame, dataset_name: str, output_path: str, cfg: dict):
        self.df = df
        self.dataset_name = dataset_name
        self.output_path = output_path
        self.cfg = cfg

    def plot(self):
        plot  = self.cfg["plot"]
        pcfg  = self.cfg["plotters"]["correlation_heatmap"]
        cols  = self.cfg["columns"]["features"]["list"]

        corr_df = self.df.filter(items=cols).corr(numeric_only=True)

        fig, ax = plt.subplots(figsize=plot["figsize"]["small"])
        sns.heatmap(
            corr_df,
            annot=True,
            fmt=".2f",
            cmap=plot["color_palette"] if plot["color_palette"] in ("coolwarm", "vlag", "icefire")
                 else "coolwarm",
            center=0,
            ax=ax,
        )
        ax.set_title(f"Feature Correlation with Prediction Error ({self.dataset_name})")
        plt.tight_layout()
        plt.savefig(f"{self.output_path}/{pcfg['filename']}", dpi=plot["dpi"])
        plt.close(fig)
