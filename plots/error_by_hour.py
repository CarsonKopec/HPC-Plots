import matplotlib.pyplot as plt
import seaborn as sns
from pandas import DataFrame


class ErrorByHour:
    def __init__(self, df: DataFrame, dataset_name: str, output_path: str, cfg: dict):
        self.df = df
        self.dataset_name = dataset_name
        self.output_path = output_path
        self.cfg = cfg

    def plot(self):
        plot  = self.cfg["plot"]
        pcfg  = self.cfg["plotters"]["error_by_hour"]
        error = self.cfg["columns"]["error"]   # {"LGBM": "signed_diff...", "SVR": ...}

        error_cols = list(error.values())
        hourly = self.df.groupby("hour")[error_cols].mean().reset_index()

        fig, ax = plt.subplots(figsize=plot["figsize"]["medium"])
        for label, col in error.items():
            sns.lineplot(data=hourly, x="hour", y=col, label=f"{label} Error", ax=ax)

        ax.axhline(0, color="white", linestyle="--", linewidth=1)
        ax.set_title(f"Average Prediction Error by Hour of Day ({self.dataset_name})")
        ax.set_xlabel("Hour")
        ax.set_ylabel("Signed Error (kWh)")
        plt.tight_layout()
        plt.savefig(f"{self.output_path}/{pcfg['filename']}", dpi=plot["dpi"])
        plt.close(fig)
