import matplotlib.pyplot as plt
import seaborn as sns
from pandas import DataFrame


class ErrorByDOW:
    def __init__(self, df: DataFrame, dataset_name: str, output_path: str, cfg: dict):
        self.df = df
        self.dataset_name = dataset_name
        self.output_path = output_path
        self.cfg = cfg

    def plot(self):
        plot  = self.cfg["plot"]
        pcfg  = self.cfg["plotters"]["error_by_dow"]
        error = self.cfg["columns"]["error"]   # {"LGBM": col, "SVR": col}

        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        melted = self.df.melt(
            id_vars=["dow"],
            value_vars=list(error.values()),
            var_name="Model",
            value_name="error",
        )
        # Replace raw column names with short labels
        col_to_label = {col: label for label, col in error.items()}
        melted["Model"] = melted["Model"].map(col_to_label)

        fig, ax = plt.subplots(figsize=plot["figsize"]["medium"])
        sns.boxplot(data=melted, x="dow", y="error", hue="Model", ax=ax, order=day_order)

        ax.axhline(0, linestyle="--", linewidth=1)
        ax.set_title(f"Prediction Error by Day of Week ({self.dataset_name})")
        ax.set_xlabel("Day")
        ax.set_ylabel("Signed Error (kWh)")
        plt.xticks(rotation=30)
        plt.tight_layout()
        plt.savefig(f"{self.output_path}/{pcfg['filename']}", dpi=plot["dpi"])
        plt.close(fig)
