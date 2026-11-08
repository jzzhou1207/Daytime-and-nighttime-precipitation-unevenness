# %% 
# # Decomposition of Daytime-Nighttime Precipitation Unevenness (UI) Contrast (Figure 3)
# This script calculates and visualizes the spatial and zonal contributions of 
# total precipitation (UI_R) and relative unevenness (UI_RE) to the daytime-nighttime 
# unevenness index (UI) contrast during El Niño and La Niña phases.

# %%
import os
import glob
import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LatitudeFormatter, LongitudeFormatter
from pathlib import Path
BASE_DIR = Path("/data1/jzzhou/precipitation/season/Daytime-and-nighttime-precipitation-unevenness/")
os.chdir(BASE_DIR)
# ==============================================================================
# 0. Global Configuration & File Paths
# ==============================================================================
# Replace with the local directory containing the NetCDF datasets from Figshare
DATA_DIR = BASE_DIR / "data"

# ==============================================================================
# 0. Path Configuration
# ==============================================================================
BASE_DIR = "/data1"

# Original data paths preserved under BASE_DIR
COORD_NC_PATH = os.path.join(DATA_DIR, "fig2_3_4/annual_pre/annual_precipitation_2001.nc")
YEARLY_PREC_PATH = os.path.join(DATA_DIR, "fig2_3_4/years_01_22.nc")
D_LIGHT_FOLDER = os.path.join(DATA_DIR, "fig2_3_4/D_index_light/")
D_NIGHT_FOLDER = os.path.join(DATA_DIR, "fig2_3_4/D_index_night/")
OUTPUT_FIG_PATH = os.path.join(DATA_DIR, "enso_unevenness_spatial_contributions.png")


# ==============================================================================
# 1. Functions
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


def plot_zonal_profile(
    ax,
    data,
    lat,
    color="black",
    fill_color="gray",
    window_deg=1.0,
    lat_bins=[60, 40, 23.5, 0, -23.5, -40, -60],
    label="",
    linestyle="-",
    show_hemisphere_means=True,
):
    """
    Calculate and plot 1-degree moving-window zonal mean profiles and interquartile shading.
    """
    if hasattr(data, "values"):
        val_array = np.array(data.values, copy=True)
    else:
        val_array = np.array(data, copy=True)
        
    lat = np.array(lat)
    half_window = window_deg / 2.0
    n_lat = len(lat)

    # 1. Calculate 1-degree moving window mean and 25th-75th percentiles
    smooth_mean = np.full(n_lat, np.nan)
    smooth_q25 = np.full(n_lat, np.nan)
    smooth_q75 = np.full(n_lat, np.nan)
    
    for i, l_val in enumerate(lat):
        idx = np.where(np.abs(lat - l_val) <= half_window)[0]
        if len(idx) > 0:
            sub_data = val_array[idx, :]
            smooth_mean[i] = np.nanmean(sub_data)
            smooth_q25[i] = np.nanpercentile(sub_data, 25)
            smooth_q75[i] = np.nanpercentile(sub_data, 75)

    ax.plot(
        lat,
        smooth_mean,
        color=color,
        linewidth=1.5,
        alpha=0.6,
        linestyle=linestyle,
        label=label,
        zorder=3,
    )
    ax.fill_between(
        lat, smooth_q25, smooth_q75, alpha=0.10, color=fill_color, zorder=1
    )

    # 2. Calculate statistics per latitude zone for axis scaling
    all_b_means, all_b_stds = [], []
    for i in range(len(lat_bins) - 1):
        lat_high = lat_bins[i]
        lat_low = lat_bins[i + 1]
        idx = np.where(
            (lat >= min(lat_low, lat_high)) & (lat <= max(lat_low, lat_high))
        )[0]

        if len(idx) > 0:
            sub_data = val_array[idx, :]
            all_b_means.append(float(np.nanmean(sub_data)))
            all_b_stds.append(float(np.nanstd(sub_data)))

    # 3. Optional hemisphere mean horizontal lines
    if show_hemisphere_means:
        nh_idx = np.where((lat >= 0) & (lat <= 60))[0]
        if len(nh_idx) > 0:
            nh_mean = float(np.nanmean(val_array[nh_idx, :]))
            ax.hlines(
                y=nh_mean, xmin=60, xmax=0, color=color,
                linewidth=1.8, linestyle="-", alpha=0.85, zorder=3,
            )

        sh_idx = np.where((lat >= -60) & (lat <= 0))[0]
        if len(sh_idx) > 0:
            sh_mean = float(np.nanmean(val_array[sh_idx, :]))
            ax.hlines(
                y=sh_mean, xmin=0, xmax=-60, color=color,
                linewidth=1.8, linestyle="-", alpha=0.85, zorder=3,
            )

    # 4. Configure axes and custom latitude ticks (60°N to 60°S)
    ax.set_xlim(60, -60)
    ax.set_xticks(lat_bins)
    lat_labels = [
        f"{abs(deg)}°N" if deg > 0 else (f"{abs(deg)}°S" if deg < 0 else "0°")
        for deg in lat_bins
    ]
    ax.set_xticklabels(lat_labels, fontsize=14, fontweight="normal")

    for b in lat_bins:
        ax.axvline(x=b, color="gray", linestyle=":", alpha=0.4, linewidth=0.8)

    ax.grid(True, linestyle=":", alpha=0.3)

    y_min = min([m - s for m, s in zip(all_b_means, all_b_stds)]) if all_b_stds else 0
    y_max = max([m + s for m, s in zip(all_b_means, all_b_stds)]) if all_b_stds else 0
    return y_min, y_max


# ==============================================================================
# 2. Data Loading & Preprocessing
# ==============================================================================
# Load primary grid coordinates
with nc.Dataset(COORD_NC_PATH, "r") as nc_precmean:
    lon = nc_precmean.variables["longitude"][:]
    lat = nc_precmean.variables["latitude"][:]
    lats = nc_precmean.variables["latitude"][:]


# Normalization constant for precipitation unevenness decomposition
daymax = 7959.97021484375

# Load annual daytime and nighttime precipitation (2001-2022)
with nc.Dataset(YEARLY_PREC_PATH, "r") as ds:
    dayprepyearly = ds.variables["dayprec"][:]
    nightprepyearly = ds.variables["nightprec"][:]

# Load annual relative unevenness index (D_daily) for daytime and nighttime
file_prefix = "concatenated_daily_precipitation_"
daytime_re_daily_yearly, _ = load_annual_variables(
    D_LIGHT_FOLDER, file_prefix, "D_daily", "D_monthly"
)
nighttime_re_daily_yearly, _ = load_annual_variables(
    D_NIGHT_FOLDER, file_prefix, "D_daily", "D_monthly"
)


# ==============================================================================
# 3. ENSO Phase Classification & UI Decomposition
# ==============================================================================
start_year = 2001
years = np.arange(2001, 2023)

elnino_years = [2002, 2004, 2009, 2014, 2015, 2018, 2019]
lanina_years = [2007, 2008, 2010, 2011, 2020, 2021, 2022]
neutral_years = [y for y in years if y not in elnino_years and y not in lanina_years]

elnino_idx = [y - start_year for y in elnino_years]
lanina_idx = [y - start_year for y in lanina_years]
neutral_idx = [y - start_year for y in neutral_years]

# Decompose daytime-nighttime UI contrast into precipitation amount (UI_R) 
# and relative unevenness (UI_RE) contributions
UI_R_el = (
    (dayprepyearly[elnino_idx, :, :] - nightprepyearly[elnino_idx, :, :])
    * (daytime_re_daily_yearly[elnino_idx, :, :] + nighttime_re_daily_yearly[elnino_idx, :, :])
    / (2 * daymax)
)
UI_R_la = (
    (dayprepyearly[lanina_idx, :, :] - nightprepyearly[lanina_idx, :, :])
    * (daytime_re_daily_yearly[lanina_idx, :, :] + nighttime_re_daily_yearly[lanina_idx, :, :])
    / (2 * daymax)
)
UI_R_ne = (
    (dayprepyearly[neutral_idx, :, :] - nightprepyearly[neutral_idx, :, :])
    * (daytime_re_daily_yearly[neutral_idx, :, :] + nighttime_re_daily_yearly[neutral_idx, :, :])
    / (2 * daymax)
)

UI_RE_el = (
    (daytime_re_daily_yearly[elnino_idx, :, :] - nighttime_re_daily_yearly[elnino_idx, :, :])
    * (dayprepyearly[elnino_idx, :, :] + nightprepyearly[elnino_idx, :, :])
    / (2 * daymax)
)
UI_RE_la = (
    (daytime_re_daily_yearly[lanina_idx, :, :] - nighttime_re_daily_yearly[lanina_idx, :, :])
    * (dayprepyearly[lanina_idx, :, :] + nightprepyearly[lanina_idx, :, :])
    / (2 * daymax)
)
UI_RE_ne = (
    (daytime_re_daily_yearly[neutral_idx, :, :] - nighttime_re_daily_yearly[neutral_idx, :, :])
    * (dayprepyearly[neutral_idx, :, :] + nightprepyearly[neutral_idx, :, :])
    / (2 * daymax)
)

# Multi-year mean spatial fields for each ENSO phase
UI_R_el_mean = np.nanmean(UI_R_el, axis=0)
UI_R_la_mean = np.nanmean(UI_R_la, axis=0)
UI_R_ne_mean = np.nanmean(UI_R_ne, axis=0)

UI_RE_el_mean = np.nanmean(UI_RE_el, axis=0)
UI_RE_la_mean = np.nanmean(UI_RE_la, axis=0)
UI_RE_ne_mean = np.nanmean(UI_RE_ne, axis=0)

# Calculate relative percentage contributions across latitude zones
lat_bins = [-60, -40, -23.5, 0, 23.5, 40, 60]
relative_UI_R_el, relative_UI_R_la, relative_UI_R_ne = [], [], []
relative_UI_RE_el, relative_UI_RE_la, relative_UI_RE_ne = [], [], []

for i in range(len(lat_bins) - 1):
    lat_min, lat_max = lat_bins[i], lat_bins[i + 1]
    lat_mask = (lats >= lat_min) & (lats < lat_max)
    
    r_el = np.abs(np.nanmean(UI_R_el_mean[lat_mask]))
    re_el = np.abs(np.nanmean(UI_RE_el_mean[lat_mask]))
    
    r_la = np.abs(np.nanmean(UI_R_la_mean[lat_mask]))
    re_la = np.abs(np.nanmean(UI_RE_la_mean[lat_mask]))
    
    r_ne = np.abs(np.nanmean(UI_R_ne_mean[lat_mask]))
    re_ne = np.abs(np.nanmean(UI_RE_ne_mean[lat_mask]))
    
    relative_UI_R_el.append(r_el / (r_el + re_el))
    relative_UI_RE_el.append(re_el / (r_el + re_el))
    
    relative_UI_R_la.append(r_la / (r_la + re_la))
    relative_UI_RE_la.append(re_la / (r_la + re_la))
    
    relative_UI_R_ne.append(r_ne / (r_ne + re_ne))
    relative_UI_RE_ne.append(re_ne / (r_ne + re_ne))


# ==============================================================================
# 4. Figure Generation (Figure 3)
# ==============================================================================
fig = plt.figure(figsize=(14, 5.5), dpi=120)
gs = fig.add_gridspec(
    2, 2, wspace=0.2, hspace=0.05, left=0.05, right=0.95, top=0.94, bottom=0.05
)

proj = ccrs.PlateCarree()
region_plot = [-180, 180, -60, 60]

ax1 = fig.add_subplot(gs[0, 0], projection=proj)
ax2 = fig.add_subplot(gs[1, 0], projection=proj)
ax3 = fig.add_subplot(gs[0, 1], projection=proj)
ax4 = fig.add_subplot(gs[1, 1], projection=proj)

for ax in [ax1, ax2, ax3, ax4]:
    ax.coastlines(resolution="110m", color="black", linewidth=0.8)
    ax.set_extent(region_plot, crs=proj)

pos2 = ax2.get_position()
cbar2 = fig.add_axes([pos2.x0 + 0.325, pos2.y0 - 0.08, pos2.width * 0.6, 0.02])

clat_zones = fig.add_axes([pos2.x0, pos2.y0 - 0.6, pos2.width, pos2.height * 1.2])
clat_zones2 = fig.add_axes([pos2.x0 + 0.47, pos2.y0 - 0.6, pos2.width, pos2.height * 1.2])

# --- Plot Zonal Profiles (Panels c & f) ---
curves_config_el = [
    (UI_R_el_mean, "#D55E00", "#D55E00", r" $\Delta UI^{EL}_{R}$", "-"),
    (UI_RE_el_mean, "#431D00", "#431D00", r" $\Delta UI^{EL}_{RE}$", "--"),
]
curves_config_la = [
    (UI_R_la_mean, "#0072B2", "#0072B2", r" $\Delta UI^{LA}_{R}$", "-"),
    (UI_RE_la_mean, "#003452", "#003452", r" $\Delta UI^{LA}_{RE}$", "--"),
]

y_mins, y_maxs = [], []
custom_lat_bins = [60, 40, 23.5, 0, -23.5, -40, -60]
clat_zones.set_xticklabels([])
clat_zones.set_yticklabels([])

# Panel c: El Niño Zonal Profile
for d, c, fc, lbl, line in curves_config_el:
    mi, ma = plot_zonal_profile(
        clat_zones, d, lat, color=c, fill_color=fc, lat_bins=custom_lat_bins,
        label=lbl, linestyle=line, show_hemisphere_means=False,
    )
    y_mins.append(mi)
    y_maxs.append(ma)

g_min, g_max = min(y_mins), max(y_maxs)
pad = (g_max - g_min) * 0.1
clat_zones.set_ylim(g_min - pad, g_max + pad)
clat_zones.axhline(0, color="gray", linewidth=0.8, linestyle="--")
clat_zones.set_yscale("symlog", linthresh=0.004)
clat_zones.set_xlabel("Latitude", fontsize=12, fontweight="normal", labelpad=5)
clat_zones.set_ylabel("Contributions", fontsize=12, fontweight="normal", labelpad=5)
clat_zones.legend(
    loc="upper right", ncols=2, frameon=True, facecolor="none",
    framealpha=0.85, fontsize=12, edgecolor="none", bbox_to_anchor=(1.01, 1.2),
)

# Panel f: La Niña Zonal Profile
for d, c, fc, lbl, line in curves_config_la:
    mi, ma = plot_zonal_profile(
        clat_zones2, d, lat, color=c, fill_color=fc, lat_bins=custom_lat_bins,
        label=lbl, linestyle=line, show_hemisphere_means=False,
    )
    y_mins.append(mi)
    y_maxs.append(ma)

g_min, g_max = min(y_mins), max(y_maxs)
pad = (g_max - g_min) * 0.1
clat_zones2.set_ylim(g_min - pad, g_max + pad)
clat_zones2.axhline(0, color="gray", linewidth=0.8, linestyle="--")
clat_zones2.set_yscale("symlog", linthresh=0.004)
clat_zones2.set_xlabel("Latitude", fontsize=12, fontweight="normal", labelpad=5)
clat_zones2.set_ylabel("Contributions", fontsize=12, fontweight="normal", labelpad=5)
clat_zones2.legend(
    loc="upper right", ncols=2, frameon=True, facecolor="none",
    framealpha=0.85, fontsize=12, edgecolor="none", bbox_to_anchor=(1.01, 1.2),
)

# Annotate relative percentage contributions in each latitude zone
lat_centers = (np.array(lat_bins[:-1]) + np.array(lat_bins[1:])) / 2

# El Niño annotations
color_r_el, color_re_el = "#D55E00", "#431D00"
for lat_text, r_val, re_val in zip(lat_centers, relative_UI_R_el[::-1], relative_UI_RE_el[::-1]):
    clat_zones.text(
        x=lat_text, y=0.9, s=r"$\Delta UI^{EL}_R$: " + f"{r_val * 100:.1f}%",
        color=color_r_el, transform=clat_zones.get_xaxis_transform(),
        fontsize=8, horizontalalignment="center", verticalalignment="bottom", fontweight="bold",
    )
    clat_zones.text(
        x=lat_text, y=0.01, s=r"$\Delta UI^{EL}_{RE}$: " + f"{re_val * 100:.1f}%",
        color=color_re_el, transform=clat_zones.get_xaxis_transform(),
        fontsize=8, horizontalalignment="center", verticalalignment="bottom", fontweight="bold",
    )

# La Niña annotations
color_r_la, color_re_la = "#0072B2", "#003452"
for lat_text, r_val, re_val in zip(lat_centers, relative_UI_R_la[::-1], relative_UI_RE_la[::-1]):
    clat_zones2.text(
        x=lat_text, y=0.9, s=r"$\Delta UI^{LA}_R$: " + f"{r_val * 100:.1f}%",
        color=color_r_la, transform=clat_zones2.get_xaxis_transform(),
        fontsize=8, horizontalalignment="center", verticalalignment="bottom", fontweight="bold",
    )
    clat_zones2.text(
        x=lat_text, y=0.01, s=r"$\Delta UI^{LA}_{RE}$: " + f"{re_val * 100:.1f}%",
        color=color_re_la, transform=clat_zones2.get_xaxis_transform(),
        fontsize=8, horizontalalignment="center", verticalalignment="bottom", fontweight="bold",
    )

# --- Plot Spatial Maps (Panels a, b, d, e) ---
mesh_kwargs = dict(transform=proj, cmap="RdBu_r", vmin=-0.05, vmax=0.05)

im1 = ax1.pcolormesh(lon, lat, UI_R_el_mean, **mesh_kwargs)
im2 = ax2.pcolormesh(lon, lat, UI_RE_el_mean, **mesh_kwargs)
im3 = ax3.pcolormesh(lon, lat, UI_R_la_mean, **mesh_kwargs)
im4 = ax4.pcolormesh(lon, lat, UI_RE_la_mean, **mesh_kwargs)

# Titles
title_kwargs = dict(fontsize=14, fontweight="normal", loc="left", x=0, y=1.02)
ax1.set_title(r"a. $\Delta UI^{EL}_{R}$", **title_kwargs)
ax2.set_title(r"b. $\Delta UI^{EL}_{RE}$", **title_kwargs)
clat_zones.set_title(r"c. Latitude zones", **title_kwargs)
ax3.set_title(r"d. $\Delta UI^{LA}_{R}$", **title_kwargs)
ax4.set_title(r"e. $\Delta UI^{LA}_{RE}$", **title_kwargs)
clat_zones2.set_title(r"f. Latitude zones", **title_kwargs)

# Colorbar
plt.colorbar(
    im4, shrink=0.93, orientation="horizontal", extend="both",
    pad=0.035, aspect=30, cax=cbar2,
)

# Map Grid Ticks and Formatters
yticks = np.arange(region_plot[-2], region_plot[-1] + 1, 30)
for ax in [ax1, ax3]:
    ax.set_xticks([-120, 0, 120], crs=proj)
    ax.set_yticks(yticks, crs=proj)
    ax.yaxis.set_major_formatter(LatitudeFormatter())
    ax.tick_params(axis="y", labelsize=12)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_xticklabels([])

for ax in [ax2, ax4]:
    ax.set_xticks([-120, 0, 120], crs=proj)
    ax.set_yticks(yticks, crs=proj)
    ax.xaxis.set_major_formatter(LongitudeFormatter())
    ax.yaxis.set_major_formatter(LatitudeFormatter())
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(axis="y", labelsize=12)
    ax.tick_params(axis="x", labelsize=12)

# Save figure (uncomment to export)
# plt.savefig(OUTPUT_FIG_PATH, format="png", dpi=600, bbox_inches="tight")
# %%