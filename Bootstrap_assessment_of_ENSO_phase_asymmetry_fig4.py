# %% [markdown]
# # Bootstrap Assessment of ENSO Phase Asymmetry in Subtropical UI (Figure 4)
# This script evaluates the daytime-nighttime precipitation unevenness index (UI)
# contrast and its daytime/nighttime anomalies across ENSO phases over the Northern 
# Hemisphere subtropics (23.5°N–40°N) using non-parametric bootstrap resampling.

# %%
import os
import glob
import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy import stats
from pathlib import Path
BASE_DIR = Path("/data1/jzzhou/precipitation/season/Daytime-and-nighttime-precipitation-unevenness/")
os.chdir(BASE_DIR)
# ==============================================================================
# 0. Global Configuration & File Paths
# ==============================================================================
# Replace with the local directory containing the NetCDF datasets from Figshare
DATA_DIR = BASE_DIR / "data" / "fig2_3_4"
OUTPUT_DIR = Path("/")

# ==============================================================================
# 0. Path Configuration
# ==============================================================================
BASE_DIR = "/data1"

# Original data paths preserved under BASE_DIR
COORD_NC_PATH = os.path.join(DATA_DIR, "annual_pre/annual_precipitation_2001.nc")
S_LIGHT_FOLDER = os.path.join(DATA_DIR, "dsi_nightmax/")
S_NIGHT_FOLDER = os.path.join(DATA_DIR, "S_night_index/")
OUTPUT_FIG_PATH = os.path.join(
    OUTPUT_DIR, "enso_unevenness_subtropics_bootstrap.png"
)


# ==============================================================================
# 1. Helper Functions
# ==============================================================================
def load_annual_variables(folder_path, file_prefix, var1_name, var2_name):
    """
    Load and stack annual 2D variables from NetCDF files in chronological order.
    """
    file_pattern = os.path.join(folder_path, f"{file_prefix}*.nc")
    nc_files = sorted(glob.glob(file_pattern))
    
    var1_list, var2_list = [], []
    for nc_file in nc_files:
        with nc.Dataset(nc_file, "r") as ds:
            var1_data = np.squeeze(ds.variables[var1_name][:])
            var2_data = np.squeeze(ds.variables[var2_name][:])
            var1_list.append(var1_data)
            var2_list.append(var2_data)
            
    return np.stack(var1_list, axis=0), np.stack(var2_list, axis=0)


def get_boot_distribution(data, n_boot=1000):
    """
    Generate bootstrap resampling distribution of the sample mean.
    """
    n = len(data)
    return np.array(
        [np.mean(np.random.choice(data, size=n, replace=True)) for _ in range(n_boot)]
    )


# ==============================================================================
# 2. Data Loading & Preprocessing
# ==============================================================================
# Load primary grid latitude coordinates
with nc.Dataset(COORD_NC_PATH, "r") as nc_precmean:
    lat = nc_precmean.variables["latitude"][:]

# Load annual unevenness index (S_daily / UI) for daytime and nighttime (2001-2022)
file_prefix = "concatenated_daily_precipitation_"
daytime_dsi_daily_yearly, _ = load_annual_variables(
    S_LIGHT_FOLDER, file_prefix, "S_daily", "S_monthly"
)
nighttime_dsi_daily_yearly, _ = load_annual_variables(
    S_NIGHT_FOLDER, file_prefix, "S_daily", "S_monthly"
)


# ==============================================================================
# 3. ENSO Classification & Subtropical Spatial Averaging (23.5°N–40°N)
# ==============================================================================
start_year = 2001
years = np.arange(2001, 2023)

elnino_years = [2002, 2004, 2009, 2014, 2015, 2018, 2019]
lanina_years = [2007, 2008, 2010, 2011, 2020, 2021, 2022]
neutral_years = [y for y in years if y not in elnino_years and y not in lanina_years]

elnino_idx = [y - start_year for y in elnino_years]
lanina_idx = [y - start_year for y in lanina_years]
neutral_idx = [y - start_year for y in neutral_years]

# Mask for Northern Hemisphere subtropics (23.5°N to 40°N)
lat_mask = (lat >= 23.5) & (lat <= 40.0)
spatial_axes = (1, 2)

ts_day_spatial = np.nanmean(daytime_dsi_daily_yearly[:, lat_mask, :], axis=spatial_axes)
ts_night_spatial = np.nanmean(nighttime_dsi_daily_yearly[:, lat_mask, :], axis=spatial_axes)

# --- Panel (a) Data: Absolute Daytime-Nighttime UI Contrast (Day - Night) ---
dui_yearly = ts_day_spatial - ts_night_spatial
neu_dui = dui_yearly[neutral_idx]
el_dui = dui_yearly[elnino_idx]
la_dui = dui_yearly[lanina_idx]

categories_left = ["All year", "Neutral", "El Niño", "La Niña"]
data_left = [dui_yearly, neu_dui, el_dui, la_dui]

# --- Panel (b) Data: Daytime and Nighttime UI Anomalies Relative to Neutral Years ---
neu_day_base = np.nanmean(ts_day_spatial[neutral_idx])
neu_night_base = np.nanmean(ts_night_spatial[neutral_idx])

el_day_anom = ts_day_spatial[elnino_idx] - neu_day_base
el_night_anom = ts_night_spatial[elnino_idx] - neu_night_base
la_day_anom = ts_day_spatial[lanina_idx] - neu_day_base
la_night_anom = ts_night_spatial[lanina_idx] - neu_night_base


# ==============================================================================
# 4. Bootstrap Resampling
# ==============================================================================
np.random.seed(42)
N_BOOT = 1000

# Bootstrap distributions for Panel (a)
boot_dists_left = [get_boot_distribution(g, n_boot=N_BOOT) for g in data_left]

# Bootstrap distributions for Panel (b)
boot_el_day = get_boot_distribution(el_day_anom, n_boot=N_BOOT)
boot_el_night = get_boot_distribution(el_night_anom, n_boot=N_BOOT)
boot_la_day = get_boot_distribution(la_day_anom, n_boot=N_BOOT)
boot_la_night = get_boot_distribution(la_night_anom, n_boot=N_BOOT)


# ==============================================================================
# 5. Figure Generation (Figure 4)
# ==============================================================================
fig, (ax1, ax2) = plt.subplots(
    1,
    2,
    figsize=(8.5, 4.2),
    dpi=300,
    sharey=False,
    gridspec_kw={"wspace": 0.15, "width_ratios": [1.1, 0.9]},
)

# ------------------ Panel (a): Bootstrap KDE of ΔUI ------------------
colors_left = ["#000000", "#8D8181", "#d7191c", "#2b83ba"]

for dist, name, color in zip(boot_dists_left, categories_left, colors_left):
    kde = stats.gaussian_kde(dist)
    x_grid = np.linspace(np.min(dist) - 0.001, np.max(dist) + 0.001, 400)
    y_kde = kde(x_grid)

    ax1.plot(x_grid, y_kde, color=color, lw=1.0, label=name, zorder=3)
    ax1.fill_between(x_grid, 0, y_kde, color=color, alpha=0.40, zorder=2)

    mean_val = np.mean(dist)
    ax1.axvline(x=mean_val, linestyle="--", color=color, zorder=4)

ax1.set_ylabel("Bootstrap Probability Density", fontsize=11)
ax1.set_xlabel(r"$\Delta\text{UI}$", fontsize=11, fontweight="normal")
ax1.set_xticks([-0.002, -0.001, 0, 0.001, 0.002])
ax1.set_xticklabels([-0.002, -0.001, 0, 0.001, 0.002], fontsize=9.5, fontweight="normal")
ax1.set_xlim(-0.002, 0.002)
ax1.set_ylim(0, 1800)

ax1.axhline(0, color="black", linewidth=0.5, linestyle="--", alpha=0.6, zorder=1)
ax1.grid(axis="x", linestyle=":", alpha=0.6)
ax1.grid(False, axis="y", linestyle=":", alpha=0.4)
ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)
ax1.spines["left"].set_visible(True)
ax1.spines["bottom"].set_visible(True)

ax1.legend(
    frameon=True, facecolor="white", edgecolor="none",
    fontsize=8.5, bbox_to_anchor=(0.7, 0.8),
)

# ------------------ Panel (b): Daytime vs. Nighttime UI Anomalies ------------------
right_items = [
    ("El Niño Day", boot_el_day, 1.2, "#de9e83"),
    ("El Niño Night", boot_el_night, 0.8, "#142f83"),
    ("La Niña Day", boot_la_day, -0.8, "#de9e83"),
    ("La Niña Night", boot_la_night, -1.2, "#142f83"),
]

for name, dist, y_pos, color in right_items:
    mean_val = np.mean(dist)
    ci_95_low, ci_95_high = np.percentile(dist, 2.5), np.percentile(dist, 97.5)
    ci_80_low, ci_80_high = np.percentile(dist, 10), np.percentile(dist, 90)

    # 95% confidence interval (thin line)
    ax2.hlines(
        y_pos, ci_95_low, ci_95_high,
        color=color, linewidth=1.5, alpha=0.6, zorder=2,
    )
    # 80% confidence interval (thick line)
    ax2.hlines(
        y_pos, ci_80_low, ci_80_high,
        color=color, linewidth=3.8, alpha=0.9, zorder=3,
    )
    # Bootstrap mean marker
    ax2.plot(
        mean_val, y_pos, "o",
        color="white", markeredgecolor=color,
        markeredgewidth=2.0, markersize=6.5, zorder=4,
    )

ax2.axvline(0, color="gray", linestyle="--", linewidth=0.9, zorder=1)
ax2.axhline(0, color="black", linewidth=0.5, linestyle="--", alpha=0.6, zorder=1)

ax2.set_yticks([1.0, -1.0])
ax2.set_yticklabels(["El Niño", "La Niña"], fontsize=10, fontweight="bold")
ax2.set_ylim(-2, 2)
ax2.set_xlabel("UI Anomaly", fontsize=11)

ax2.yaxis.set_visible(True)
ax2.yaxis.tick_right()
ax2.yaxis.set_label_position("right")
ax2.set_ylabel("", fontsize=11, fontweight="normal")

ax2.spines["top"].set_visible(False)
ax2.spines["left"].set_visible(True)
ax2.spines["left"].set_position(("outward", 10))
ax2.spines["right"].set_visible(True)
ax2.spines["bottom"].set_visible(True)
ax2.grid(False, axis="y", linestyle=":", alpha=0.4)

custom_legend = [
    Line2D(
        [0], [0], marker="o", color="w",
        markeredgecolor="#de9e83", markeredgewidth=1.8, label="Day Anomaly",
    ),
    Line2D(
        [0], [0], marker="o", color="w",
        markeredgecolor="#142f83", markeredgewidth=1.8, label="Night Anomaly",
    ),
    Line2D([0], [0], color="black", lw=3.8, label="80% CI"),
    Line2D([0], [0], color="black", lw=1.5, alpha=0.6, label="95% CI"),
]
ax2.legend(
    handles=custom_legend, frameon=True, facecolor="white",
    edgecolor="none", fontsize=8, bbox_to_anchor=(0.5, 0.38),
)

# ------------------ Panel Labels (a) and (b) ------------------
ax1.text(
    -0.1, 1.1, "a", transform=ax1.transAxes,
    fontsize=11, fontweight="bold", va="top", ha="left",
)
ax2.text(
    0.0, 1.1, "b", transform=ax2.transAxes,
    fontsize=11, fontweight="bold", va="top", ha="left",
)

# Save figure (uncomment to export)
# plt.savefig(OUTPUT_FIG_PATH, format="png", dpi=600, bbox_inches="tight")
# %%