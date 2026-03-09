import matplotlib.pyplot as plt
import seaborn as sns
from pandas import DataFrame


# Valid (orientation, location) combinations → cbar_kws
_COLORBAR_SIDE = {
    ("vertical",   "right"):  dict(location="right"),
    ("vertical",   "left"):   dict(location="left"),
    ("horizontal", "bottom"): dict(location="bottom"),
    ("horizontal", "top"):    dict(location="top"),
}


class CorrelationHeatmap:
    def __init__(self, df: DataFrame, dataset_name: str, output_path: str, cfg: dict):
        self.df           = df
        self.dataset_name = dataset_name
        self.output_path  = output_path
        self.cfg          = cfg

    # ── Public ────────────────────────────────────────────────────────────────

    def plot(self):
        pcfg        = self.cfg["plotters"]["correlation_heatmap"]
        feature_map = self.cfg["columns"]["features"]  # {1: "col_name", 2: ...}

        # Normalise keys to int so config authors can use either 1 or "1"
        feature_map = {int(k): v for k, v in feature_map.items()}
        all_ids     = list(feature_map.keys())

        row_ids, col_ids = self._resolve_axes(pcfg, all_ids)

        # Build correlation matrix over the union of both axes
        involved_cols = list(dict.fromkeys(
            [feature_map[i] for i in row_ids] +
            [feature_map[i] for i in col_ids]
        ))
        corr_df = self.df.filter(items=involved_cols).corr(numeric_only=True)

        # Keep original column names for display; map IDs back to names for slicing
        id_to_col  = feature_map
        row_labels = [id_to_col[i] for i in row_ids]
        col_labels = [id_to_col[i] for i in col_ids]

        max_rows = int(pcfg.get("max_rows", 0))
        max_cols = int(pcfg.get("max_cols", 0))

        if max_rows == 0 and max_cols == 0:
            self._plot_single(corr_df, row_labels, col_labels, pcfg)
        else:
            self._plot_tiled(corr_df, row_labels, col_labels,
                             max_rows or len(row_labels),
                             max_cols or len(col_labels),
                             pcfg)

    # ── Axis resolution ───────────────────────────────────────────────────────

    def _resolve_axes(self, pcfg: dict, all_ids: list[int]) -> tuple[list, list]:
        row_ids   = [int(i) for i in pcfg.get("row_ids", all_ids)]
        col_ids   = [int(i) for i in pcfg.get("col_ids", all_ids)]
        lock_rows = bool(pcfg.get("lock_rows", False))
        lock_cols = bool(pcfg.get("lock_cols", False))

        assigned = set(row_ids) | set(col_ids)
        overflow = [i for i in all_ids if i not in assigned]

        if not lock_rows and not lock_cols:
            return all_ids, all_ids

        if lock_rows and not lock_cols:
            col_ids = col_ids + overflow

        if lock_cols and not lock_rows:
            row_ids = row_ids + overflow

        return row_ids, col_ids

    # ── Sizing ────────────────────────────────────────────────────────────────

    def _figsize_for(self, n_rows: int, n_cols: int, pcfg: dict,
                     extra_w: float = 2.5, extra_h: float = 2.0) -> tuple[float, float]:
        """
        Scale figure size to content so cells stay compact regardless of
        how many features are on each axis.
        cell_width / cell_height are configurable in defaults.toml under
        [plotters.correlation_heatmap].
          extra_w / extra_h: padding budget for axis labels, colorbar, title.
        """
        cw = float(pcfg.get("cell_width",  0.7))
        ch = float(pcfg.get("cell_height", 0.5))
        return (cw * n_cols + extra_w, ch * n_rows + extra_h)

    # ── Colorbar ──────────────────────────────────────────────────────────────

    def _colorbar_kwargs(self, pcfg: dict) -> dict:
        cb       = pcfg.get("colorbar", {})
        orient   = cb.get("orientation", "vertical")
        location = cb.get("location", "right")
        shrink   = float(cb.get("shrink", 0.8))
        pad      = float(cb.get("pad", 0.02))
        side_kws = _COLORBAR_SIDE.get((orient, location), dict(location="right"))
        return dict(orientation=orient, shrink=shrink, pad=pad, **side_kws)

    # ── Drawing ───────────────────────────────────────────────────────────────

    def _draw_heatmap(self, ax, corr_slice, pcfg: dict) -> None:
        sns.heatmap(
            corr_slice,
            annot=True,
            fmt=".2f",
            cmap=pcfg.get("cmap", "coolwarm"),
            center=0,
            ax=ax,
            cbar_kws=self._colorbar_kwargs(pcfg),
        )

    def _slice(self, corr_df, row_names: list, col_names: list):
        valid_rows = [r for r in row_names if r in corr_df.index]
        valid_cols = [c for c in col_names if c in corr_df.columns]
        return corr_df.loc[valid_rows, valid_cols]

    def _plot_single(self, corr_df, row_labels, col_labels, pcfg: dict) -> None:
        sliced  = self._slice(corr_df, row_labels, col_labels)
        figsize = self._figsize_for(len(sliced.index), len(sliced.columns), pcfg)
        fig, ax = plt.subplots(figsize=figsize)
        self._draw_heatmap(ax, sliced, pcfg)
        ax.set_title(
            f"Feature Correlation with Prediction Error ({self.dataset_name})"
        )
        self._save(fig, pcfg)

    def _plot_tiled(self, corr_df, row_labels: list, col_labels: list,
                    max_rows: int, max_cols: int, pcfg: dict) -> None:
        row_chunks  = [row_labels[i:i + max_rows] for i in range(0, len(row_labels), max_rows)]
        col_chunks  = [col_labels[i:i + max_cols] for i in range(0, len(col_labels), max_cols)]
        n_grid_rows = len(row_chunks)
        n_grid_cols = len(col_chunks)

        # Largest tile drives the per-tile figsize so all tiles are uniform
        max_r    = max(len(c) for c in row_chunks)
        max_c    = max(len(c) for c in col_chunks)
        tile_w, tile_h = self._figsize_for(max_r, max_c, pcfg)

        fig, axes = plt.subplots(
            n_grid_rows, n_grid_cols,
            figsize=(tile_w * n_grid_cols, tile_h * n_grid_rows),
            squeeze=False,
        )
        fig.suptitle(
            f"Feature Correlation with Prediction Error ({self.dataset_name})",
            fontsize=13, fontweight="bold", y=1.01,
        )

        for r_idx, r_chunk in enumerate(row_chunks):
            for c_idx, c_chunk in enumerate(col_chunks):
                ax = axes[r_idx][c_idx]
                self._draw_heatmap(ax, self._slice(corr_df, r_chunk, c_chunk), pcfg)
                ax.set_title(
                    f"Rows {r_chunk[0]}–{r_chunk[-1]}  ×  Cols {c_chunk[0]}–{c_chunk[-1]}",
                    fontsize=9,
                )

        plt.tight_layout()
        self._save(fig, pcfg)

    def _save(self, fig, pcfg: dict) -> None:
        fig.savefig(
            f"{self.output_path}/{pcfg['filename']}",
            dpi=self.cfg["plot"]["dpi"],
            bbox_inches="tight",
        )
        plt.close(fig)