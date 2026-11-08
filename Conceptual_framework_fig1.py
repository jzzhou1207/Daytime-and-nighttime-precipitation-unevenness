# %% [markdown]
# # Conceptual Framework of Precipitation Unevenness Index (UI) and Relative Entropy (RE) (Figure 1)
# This script illustrates the conceptual behavior of Relative Entropy (RE), 
# Unevenness Index (UI), and effective precipitation days (N_eff) across four 
# synthetic daily precipitation regimes:
# - (a) Low Rainfall - Many Days (LR-MD)
# - (b) Low Rainfall - Few Days (LR-FD)
# - (d) High Rainfall - Many Days (HR-MD)
# - (e) High Rainfall - Few Days (HR-FD)
# Panels (c) and (f) compare cumulative RE trajectories and final RE/UI values.

# %%
import os
import glob
import netCDF4 as nc
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

# ==============================================================================
# 0. Path & Global Configuration
# ==============================================================================
BASE_DIR = "/data1"

# Output figure path preserved under BASE_DIR
OUTPUT_FIG_PATH = os.path.join(
    BASE_DIR, "concept_RE_UI_meaning.png"
)

# Global matplotlib styling
mpl.rcParams.update(
    {
        "text.usetex": False,
        "font.sans-serif": ["Arial"],
        "mathtext.fontset": "stix",
        "font.size": 14,
    }
)


# ==============================================================================
# 1. Helper Functions
# ==============================================================================
def draw_re_ui_subgrid(fig, subgrid_slot, pair_results, title_text):
    """
    Render the nested subgrid (cumulative RE line plot + dual-axis RE/UI bar chart)
    in the right-hand column of Figure 1 (Panels c and f).
    """
    gs_sub = subgrid_slot.subgridspec(1, 2, width_ratios=[3, 1], wspace=0.3)

    ax1 = fig.add_subplot(gs_sub[0, 0])
    ax2 = fig.add_subplot(gs_sub[0, 1])

    days = np.arange(1, 366)
    colors_line = ["#E1959A", "#2ca02c"]

    # --- Left sub-panel: Cumulative RE trajectories ---
    for idx, res in enumerate(pair_results):
        scenario_short_name = res["name"].split(".", 1)[-1].strip()
        ax1.plot(
            days,
            res["re_cum"],
            label=f"RE ({scenario_short_name})",
            color=colors_line[idx % len(colors_line)],
            linewidth=1.2,
        )

    ax1.set_xlabel("Day of Year", fontsize=14)
    ax1.set_ylabel("Cumulative RE", fontsize=14)
    ax1.legend(loc="upper left", fontsize=14, frameon=False)
    ax1.grid(True, linestyle="--", alpha=0.4)
    ax1.set_xlim(0, 366)

    _, y_max = ax1.get_ylim()
    ax1.set_ylim(0, y_max)
    ax1.set_title(title_text, fontsize=12, fontweight="bold", loc="left")

    # Annotate effective rainy days (N_eff)
    names = [res["name"].split(".", 1)[-1].strip() for res in pair_results]
    re_vals = [res["re_val"] for res in pair_results]
    ui_vals = [res["ui_val"] for res["ui_val"] in [res["ui_val"] for res in pair_results]]
    n_eff = 365 * (2.0 ** -np.array(re_vals))

    props = dict(boxstyle="round,pad=0.4", facecolor="none", alpha=0.9, edgecolor="1")
    ax1.text(
        0.03, 0.65, f"$N_{{eff}}$ = {n_eff[0]:.1f} days",
        transform=ax1.transAxes, fontsize=12, verticalalignment="top",
        bbox=props, color="#E1959A",
    )
    ax1.text(
        0.03, 0.75, f"$N_{{eff}}$ = {n_eff[1]:.1f} days",
        transform=ax1.transAxes, fontsize=12, verticalalignment="top",
        bbox=props, color="#2ca02c",
    )

    # --- Right sub-panel: Dual-axis grouped bar chart for RE and UI ---
    x = np.arange(len(names))
    width = 0.35

    # Left Y-axis: RE (Blue)
    ax2.bar(
        x - width / 2, re_vals, width,
        label="RE", color="#1f78b4", alpha=0.75, edgecolor="black",
    )
    ax2.set_ylabel("RE", fontsize=12, color="#1f78b4")
    ax2.tick_params(axis="y", labelcolor="#1f78b4", labelsize=12)
    ax2.set_xticks(x)
    ax2.set_xticklabels(names, fontsize=10, rotation=45)
    ax2.set_ylim(0, y_max)

    # Right Y-axis: UI (Red)
    ax2_right = ax2.twinx()
    ax2_right.bar(
        x + width / 2, ui_vals, width,
        label="UI", color="#d62728", alpha=0.75, edgecolor="black",
    )
    ax2_right.set_ylabel("UI", fontsize=12, color="#d62728")
    ax2_right.tick_params(axis="y", labelcolor="#d62728", labelsize=12)

    max_ui = max(ui_vals) if max(ui_vals) != 0 else 1.0
    ax2_right.set_ylim(0, max_ui * 1.2)


# ==============================================================================
# 2. Synthetic Scenarios Simulation & Main Figure Generation (Figure 1)
# ==============================================================================
total_days = 365
q_n = 1.0 / total_days
R_max = 2000.0  # Reference maximum annual precipitation (mm)

scenarios = [
    {"name": "a. LR-MD", "P_total": 100,  "rain_days": 200},
    {"name": "b. LR-FD", "P_total": 100,  "rain_days": 20},
    {"name": "d. HR-MD", "P_total": 1000, "rain_days": 200},
    {"name": "e. HR-FD", "P_total": 1000, "rain_days": 20},
]

fig = plt.figure(figsize=(18, 10))
gs_main = fig.add_gridspec(2, 3, wspace=0.2, hspace=0.3)

results = []
np.random.seed(42)  # Fixed seed for exact reproducibility

# --- Panels (a, b, d, e): Daily Precipitation Time Series ---
for i, sc in enumerate(scenarios):
    row = i // 2
    col = i % 2
    ax = fig.add_subplot(gs_main[row, col])

    P_total = sc["P_total"]
    rain_days = sc["rain_days"]

    # 1. Randomly select wet days and allocate daily amounts via exponential distribution
    rain_indices = np.random.choice(total_days, rain_days, replace=False)
    raw_rains = np.random.exponential(scale=1.0, size=rain_days)
    daily_rain = np.zeros(total_days)
    daily_rain[rain_indices] = (raw_rains / raw_rains.sum()) * P_total

    # 2. Calculate daily probability (p_dt), Relative Entropy (RE), and cumulative RE
    p_dt = daily_rain / P_total
    valid = p_dt > 0
    re_val = np.sum(p_dt[valid] * np.log2(p_dt[valid] / q_n))
    
    term = np.zeros_like(p_dt, dtype=float)
    term[valid] = p_dt[valid] * np.log2(p_dt[valid] / q_n)
    re_cum = np.cumsum(term)

    # 3. Calculate Unevenness Index (UI)
    ui_val = re_val * (P_total / R_max)

    results.append(
        {
            "name": sc["name"],
            "re_val": re_val,
            "ui_val": ui_val,
            "re_cum": re_cum,
        }
    )

    # 4. Plot daily precipitation bars
    bar_color = "#1f78b4" if P_total > 500 else "#6baed6"
    ax.bar(
        range(1, total_days + 1),
        daily_rain,
        color=bar_color,
        width=1.0,
        edgecolor="none",
        alpha=0.85,
    )

    ax.set_title(sc["name"], fontsize=12, fontweight="bold", pad=8, loc="left")
    ax.set_xlabel("Day of Year", fontsize=12)
    ax.set_ylabel("Precipitation (mm/day)", fontsize=12)
    ax.grid(True, linestyle="--", alpha=0.2)
    ax.set_xlim(0, 366)

    # Summary statistics text box
    text_str = (
        f"$R$ = {P_total} mm\n"
        f"rain days = {rain_days}\n"
        f"RE = {re_val:.3f}\n"
        f"UI = {ui_val:.3f}"
    )
    props = dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.9, edgecolor="1")
    ax.text(
        0.03, 0.96, text_str,
        transform=ax.transAxes, fontsize=12, verticalalignment="top", bbox=props,
    )

# --- Panels (c, f): Cumulative RE & Final Metrics Comparison ---
draw_re_ui_subgrid(fig, gs_main[0, 2], results[0:2], "c. RE & UI ")
draw_re_ui_subgrid(fig, gs_main[1, 2], results[2:4], "f. RE & UI ")

# Save main conceptual figure
# plt.savefig(OUTPUT_FIG_PATH, format="png", dpi=600, bbox_inches="tight")


# %%