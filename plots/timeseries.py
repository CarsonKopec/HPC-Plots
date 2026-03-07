import matplotlib.pyplot as plt
import seaborn as sns
from pandas import DataFrame


class TimeSeriesPlotter:
    def __init__(self, df: DataFrame, dataset_name: str, output_path: str, cfg: dict):
        self.df = df
        self.dataset_name = dataset_name
        self.output_path = output_path
        self.cfg = cfg

    def plot(self):
        cols   = self.cfg["columns"]
        plot   = self.cfg["plot"]
        pcfg   = self.cfg["plotters"]["timeseries"]

        date_col   = cols["date"]
        actual_col = cols["actual_energy"]
        models     = cols["models"]   # {"LGBM": "predicted_energy_kwhr_LGBM", ...}

        fig, ax = plt.subplots(figsize=plot["figsize"]["large"])
        sns.lineplot(data=self.df, x=date_col, y=actual_col, label="Actual Energy (kWh)", ax=ax)

        for label, col in models.items():
            sns.lineplot(data=self.df, x=date_col, y=col,
                         label=f"Predicted Energy (kWh - {label})", ax=ax)

        ax.set_title(f"Actual vs Predicted Energy (kWh) ({self.dataset_name})")
        ax.set_xlabel("Date")
        ax.set_ylabel("Energy (kWh)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{self.output_path}/{pcfg['filename']}", dpi=plot["dpi"])
        plt.close(fig)
