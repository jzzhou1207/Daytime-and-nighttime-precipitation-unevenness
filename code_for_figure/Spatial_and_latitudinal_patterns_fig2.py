#%%
# -*- coding: utf-8 -*-
"""
Script Name: Spatial_and_latitudinal_patterns_fig2.py
Description: 
    Calculates and plots the spatial patterns, regional/latitudinal statistics, 
    and zonal profiles of diurnal precipitation unevenness index (UI) differences 
    during El Niño, La Niña, and Neutral years (reproducing Figure 2).

Requirements:
    - numpy, netCDF4, matplotlib, cartopy

Usage:
    1. Place the required NetCDF datasets in the directory specified by `DATA_DIR`.
    2. Run the script: `python Spatial_and_latitudinal_patterns_fig2.py`
"""

import glob
import os
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LatitudeFormatter, LongitudeFormatter
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import netCDF4 as nc
import numpy as np
from pathlib import Path
BASE_DIR = Path("/data1/jzzhou/precipitation/season/Daytime-and-nighttime-precipitation-unevenness/")
os.chdir(BASE_DIR)
# ==============================================================================
# 0. Global Configuration & File Paths
# ==============================================================================
# Replace with the local directory containing the NetCDF datasets from Figshare
DATA_DIR = BASE_DIR / "data" / "fig2_3_4"
OUTPUT_DIR = Path("/")
# %%
# Specific file and folder paths used for Figure 2
COORD_FILE = os.path.join(
    DATA_DIR, "annual_pre/annual_precipitation_2001.nc"
)
DAY_DSI_DIR = os.path.join(DATA_DIR, "dsi_nightmax/")
NIGHT_DSI_DIR = os.path.join(DATA_DIR, "S_night_index/")
FILE_PREFIX = "concatenated_daily_precipitation_"

OUTPUT_FIG_PATH = os.path.join(OUTPUT_DIR, "enso_unevenness_spatial2.png")
# Study period and ENSO phase classifications (2001-2022)
START_YEAR = 2001
YEARS = np.arange(2001, 2023)
ELNINO_YEARS = [2002, 2004, 2009, 2014, 2015, 2018, 2019]
LANINA_YEARS = [2007, 2008, 2010, 2011, 2020, 2021, 2022]
NEUTRAL_YEARS = [
    y for y in YEARS if y not in ELNINO_YEARS and y not in LANINA_YEARS
]

# ==============================================================================
# 1. Helper Functions for Data Loading & Statistics
# ==============================================================================
def load_yearly_nc_data(folder_path, file_prefix, var1_name, var2_name):
    """
    Loads yearly NetCDF files from a directory and stacks them into 3D arrays.

    Parameters:
        folder_path (str): Directory path containing the .nc files.
        file_prefix (str): Filename prefix to match.
        var1_name (str): Name of the first variable to extract.
        var2_name (str): Name of the second variable to extract.

    Returns:
        tuple: Two 3D numpy arrays (N_years, Lat, Lon) for var1 and var2.
    """
    file_pattern = os.path.join(folder_path, f"{file_prefix}*.nc")
    nc_files = sorted(glob.glob(file_pattern))
    if not nc_files:
        raise FileNotFoundError(f"No files found matching pattern: {file_pattern}")

    var1_list, var2_list = [], []
    for nc_file in nc_files:
        with nc.Dataset(nc_file, "r") as ds:
            data1 = np.squeeze(ds.variables[var1_name][:])
            data2 = np.squeeze(ds.variables[var2_name][:])
            var1_list.append(data1)
            var2_list.append(data2)

    return np.stack(var1_list, axis=0), np.stack(var2_list, axis=0)


def calc_stats_for_region(
    dsi_day_3d, dsi_night_3d, elnino_idx, lanina_idx, neutral_idx, mask=None
):
    """
    Calculates relative percentage anomalies and standard errors of daytime and 
    nighttime UI during El Niño and La Niña years relative to Neutral years.

    Parameters:
        dsi_day_3d (ndarray): 3D array of daytime UI (year, lat, lon).
        dsi_night_3d (ndarray): 3D array of nighttime UI (year, lat, lon).
        elnino_idx (list): Array indices for El Niño years.
        lanina_idx (list): Array indices for La Niña years.
        neutral_idx (list): Array indices for Neutral years.
        mask (ndarray, optional): Boolean mask for latitude band subsetting.

    Returns:
        tuple: ((el_day_mean, el_day_se), (el_night_mean, el_night_se),
                (la_day_mean, la_day_se), (la_night_mean, la_night_se))
    """
    if mask is not None:
        dsi_day_sub = dsi_day_3d[:, mask, :]
        dsi_night_sub = dsi_night_3d[:, mask, :]
    else:
        dsi_day_sub = dsi_day_3d
        dsi_night_sub = dsi_night_3d

    # 1. Spatial mean time series (N_years,)
    ts_day = np.nanmean(dsi_day_sub, axis=(1, 2))
    ts_night = np.nanmean(dsi_night_sub, axis=(1, 2))

    # 2. Baseline during ENSO-neutral years
    neu_day_base = np.nanmean(ts_day[neutral_idx])
    neu_night_base = np.nanmean(ts_night[neutral_idx])

    # 3. El Niño relative anomalies (%) and standard error (SE)
    el_day_anom = ts_day[elnino_idx] - neu_day_base
    el_night_anom = ts_night[elnino_idx] - neu_night_base

    el_d_mean = np.mean(el_day_anom) / neu_day_base * 100
    el_d_se = (
        np.std(el_day_anom, ddof=1) / np.sqrt(len(el_day_anom)) / neu_day_base * 100
    )

    el_n_mean = np.mean(el_night_anom) / neu_night_base * 100
    el_n_se = (
        np.std(el_night_anom, ddof=1)
        / np.sqrt(len(el_night_anom))
        / neu_night_base
        * 100
    )

    # 4. La Niña relative anomalies (%) and standard error (SE)
    la_day_anom = ts_day[lanina_idx] - neu_day_base
    la_night_anom = ts_night[lanina_idx] - neu_night_base

    la_d_mean = np.mean(la_day_anom) / neu_day_base * 100
    la_d_se = (
        np.std(la_day_anom, ddof=1) / np.sqrt(len(la_day_anom)) / neu_day_base * 100
    )

    la_n_mean = np.mean(la_night_anom) / neu_night_base * 100
    la_n_se = (
        np.std(la_night_anom, ddof=1)
        / np.sqrt(len(la_night_anom))
        / neu_night_base
        * 100
    )

    return (
        (el_d_mean, el_d_se),
        (el_n_mean, el_n_se),
        (la_d_mean, la_d_se),
        (la_n_mean, la_n_se),
    )


def plot_zonal_profile(
    ax,
    data,
    lat,
    color="black",
    fill_color="gray",
    window_deg=1.0,
    lat_bins=(60, 40, 23.5, 0, -23.5, -40, -60),
    label="",
    show_hemisphere_means=False,
):
    """
    Plots the latitudinal (zonal) profile with a moving window average and 
    interquartile shading (25th to 75th percentile).
    """
    val_array = np.array(data.values, copy=True) if hasattr(data, "values") else np.array(data, copy=True)
    lat = np.array(lat)
    half_window = window_deg / 2.0
    n_lat = len(lat)

    # 1. Calculate 1-degree moving window mean and interquartile range
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
        linestyle="-",
        label=label,
        zorder=3,
    )
    ax.fill_between(
        lat, smooth_q25, smooth_q75, alpha=0.10, color=fill_color, zorder=1
    )

    # 2. Compute zonal band statistics for y-axis scaling
    all_b_means, all_b_stds = [], []
    for i in range(len(lat_bins) - 1):
        lat_high, lat_low = lat_bins[i], lat_bins[i + 1]
        idx = np.where(
            (lat >= min(lat_low, lat_high)) & (lat <= max(lat_low, lat_high))
        )[0]
        if len(idx) > 0:
            sub_data = val_array[idx, :]
            all_b_means.append(float(np.nanmean(sub_data)))
            all_b_stds.append(float(np.nanstd(sub_data)))

    # 3. Optional hemisphere mean lines
    if show_hemisphere_means:
        nh_idx = np.where((lat >= 0) & (lat <= 60))[0]
        if len(nh_idx) > 0:
            nh_mean = float(np.nanmean(val_array[nh_idx, :]))
            ax.hlines(
                y=nh_mean, xmin=60, xmax=0, color=color,
                linewidth=1.8, linestyle="-", alpha=0.85, zorder=3
            )
        sh_idx = np.where((lat >= -60) & (lat <= 0))[0]
        if len(sh_idx) > 0:
            sh_mean = float(np.nanmean(val_array[sh_idx, :]))
            ax.hlines(
                y=sh_mean, xmin=0, xmax=-60, color=color,
                linewidth=1.8, linestyle="-", alpha=0.85, zorder=3
            )

    # 4. Configure axis limits and ticks (60°N to 60°S)
    ax.set_xlim(60, -60)
    ax.set_xticks(lat_bins)
    lat_labels = [
        f"{abs(deg)}°N" if deg > 0 else (f"{abs(deg)}°S" if deg < 0 else "0°")
        for deg in lat_bins
    ]
    ax.set_xticklabels(lat_labels, fontsize=12, fontweight="normal")

    for b in lat_bins:
        ax.axvline(x=b, color="gray", linestyle=":", alpha=0.4, linewidth=0.8)

    ax.grid(True, linestyle=":", alpha=0.3)

    y_min = min([m - s for m, s in zip(all_b_means, all_b_stds)]) if all_b_stds else 0
    y_max = max([m + s for m, s in zip(all_b_means, all_b_stds)]) if all_b_stds else 0
    return y_min, y_max
#%%
# ==============================================================================
# 2. Main Execution Workflow
# ==============================================================================
def main():
    # --- 2.1 Load Coordinate Data ---
    with nc.Dataset(COORD_FILE, "r") as nc_coord:
        lon = nc_coord.variables["longitude"][:].copy()
        lat = nc_coord.variables["latitude"][:].copy()

    # --- 2.2 Load Daytime and Nighttime UI (S_daily) Data ---
    daytime_dsi_daily_yearly, _ = load_yearly_nc_data(
        DAY_DSI_DIR, FILE_PREFIX, "S_daily", "S_monthly"
    )
    nighttime_dsi_daily_yearly, _ = load_yearly_nc_data(
        NIGHT_DSI_DIR, FILE_PREFIX, "S_daily", "S_monthly"
    )

    # Convert calendar years to 0-based array indices
    elnino_idx = [y - START_YEAR for y in ELNINO_YEARS]
    lanina_idx = [y - START_YEAR for y in LANINA_YEARS]
    neutral_idx = [y - START_YEAR for y in NEUTRAL_YEARS]

    # --- 2.3 Calculate Spatial Difference Maps (Day - Night) ---
    en_day_map = np.nanmean(daytime_dsi_daily_yearly[elnino_idx, :, :], axis=0)
    en_night_map = np.nanmean(nighttime_dsi_daily_yearly[elnino_idx, :, :], axis=0)
    map_el_dn_diff = en_day_map - en_night_map

    la_day_map = np.nanmean(daytime_dsi_daily_yearly[lanina_idx, :, :], axis=0)
    la_night_map = np.nanmean(nighttime_dsi_daily_yearly[lanina_idx, :, :], axis=0)
    map_la_dn_diff = la_day_map - la_night_map

    ne_day_map = np.nanmean(daytime_dsi_daily_yearly[neutral_idx, :, :], axis=0)
    ne_night_map = np.nanmean(nighttime_dsi_daily_yearly[neutral_idx, :, :], axis=0)
    map_ne_dn_diff = ne_day_map - ne_night_map

    # --- 2.4 Calculate Regional & Latitudinal Band Statistics ---
    lat_bins = [60, 40, 23.5, 0, -23.5, -40, -60]
    bin_labels = [
        "40°N-60°N",
        "23.5°N-40°N",
        "0°-23.5°N",
        "23.5°S-0°",
        "40°S-23.5°S",
        "60°S-40°S",
    ]
    all_labels = ["Global"] + bin_labels

    el_day_means, el_day_stds = [], []
    el_night_means, el_night_stds = [], []
    la_day_means, la_day_stds = [], []
    la_night_means, la_night_stds = [], []

    # Global statistics (mask=None)
    el_d, el_n, la_d, la_n = calc_stats_for_region(
        daytime_dsi_daily_yearly,
        nighttime_dsi_daily_yearly,
        elnino_idx,
        lanina_idx,
        neutral_idx,
        mask=None,
    )
    el_day_means.append(el_d[0])
    el_day_stds.append(el_d[1])
    el_night_means.append(el_n[0])
    el_night_stds.append(el_n[1])
    la_day_means.append(la_d[0])
    la_day_stds.append(la_d[1])
    la_night_means.append(la_n[0])
    la_night_stds.append(la_n[1])

    # Latitudinal band statistics
    for i in range(len(lat_bins) - 1):
        lat_max, lat_min = lat_bins[i], lat_bins[i + 1]
        lat_mask = (lat >= lat_min) & (lat < lat_max)

        el_d, el_n, la_d, la_n = calc_stats_for_region(
            daytime_dsi_daily_yearly,
            nighttime_dsi_daily_yearly,
            elnino_idx,
            lanina_idx,
            neutral_idx,
            mask=lat_mask,
        )
        el_day_means.append(el_d[0])
        el_day_stds.append(el_d[1])
        el_night_means.append(el_n[0])
        el_night_stds.append(el_n[1])
        la_day_means.append(la_d[0])
        la_day_stds.append(la_d[1])
        la_night_means.append(la_n[0])
        la_night_stds.append(la_n[1])

    # ==========================================================================
    # 3. Figure Plotting (GridSpec Layout)
    # ==========================================================================
    fig = plt.figure(figsize=(16, 9))
    gs = gridspec.GridSpec(2, 2, width_ratios=[2.0, 1], hspace=0.0, wspace=0.18)

    vmin, vmax = -0.1, 0.1
    cmap = "RdBu_r"
    region_plot = [-180, 180, -60, 60]
    proj = ccrs.PlateCarree()
    x = np.arange(len(all_labels))
    width = 0.4

    # --------------------------------------------------------------------------
    # Row 1: El Niño
    # --------------------------------------------------------------------------
    # Panel a: El Niño spatial difference map
    ax1_map = fig.add_subplot(gs[0, 0], projection=proj)
    ax1_map.add_feature(cfeature.COASTLINE, linewidth=0.8, edgecolor="black")
    ax1_map.set_extent(region_plot, crs=proj)
    ax1_map.pcolormesh(
        lon,
        lat,
        map_el_dn_diff,
        transform=proj,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        shading="auto",
    )
    ax1_map.set_title(
        r"a. $\Delta UI^{EL}$",
        fontsize=14,
        fontweight="normal",
        loc="left",
        x=-0.05,
        y=1.05,
    )

    # Panel b: El Niño vs. Neutral bar chart
    fig.canvas.draw()
    ax1_bar = fig.add_subplot(gs[0, 1])
    pos_map1 = ax1_map.get_position()
    pos_bar1 = ax1_bar.get_position()
    ax1_bar.set_position(
        [pos_bar1.x0, pos_bar1.y0 + 0.04, pos_bar1.width, pos_map1.height]
    )

    ax1_bar.bar(
        x - 1.5 * width,
        el_day_means,
        width,
        yerr=el_day_stds,
        capsize=4,
        color="#de9e83",
        alpha=0.85,
        edgecolor="black",
        linewidth=0.8,
        label=r"$UI^{EL}_{dt} - UI^{NE}_{dt}$",
        error_kw={"elinewidth": 1.0, "ecolor": "black"},
    )
    ax1_bar.bar(
        x - 0.5 * width,
        el_night_means,
        width,
        yerr=el_night_stds,
        capsize=4,
        color="#293F81",
        alpha=0.85,
        edgecolor="black",
        linewidth=0.8,
        label=r"$UI^{EL}_{nt} - UI^{NE}_{nt}$",
        error_kw={"elinewidth": 1.0, "ecolor": "black"},
    )

    ax1_bar.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax1_bar.set_xticks(x + 1.0 * width)
    ax1_bar.set_xticklabels("", fontsize=11, fontweight="normal", rotation=45)
    ax1_bar.set_ylabel(r"$UI^{EL}$ vs. $UI^{NE}$ (%)", fontsize=12)
    ax1_bar.set_title(
        r"b. $UI^{EL}$ vs. $UI^{NE}$",
        fontsize=12,
        fontweight="normal",
        loc="left",
        x=-0.15,
    )
    ax1_bar.legend(frameon=False, fontsize=10, loc="lower left")
    ax1_bar.grid(axis="y", linestyle=":", alpha=0.6)

    # --------------------------------------------------------------------------
    # Row 2: La Niña
    # --------------------------------------------------------------------------
    # Panel c: La Niña spatial difference map
    ax2_map = fig.add_subplot(gs[1, 0], projection=proj)
    ax2_map.add_feature(cfeature.COASTLINE, linewidth=0.8, edgecolor="black")
    ax2_map.set_extent(region_plot, crs=proj)
    mesh2 = ax2_map.pcolormesh(
        lon,
        lat,
        map_la_dn_diff,
        transform=proj,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        shading="auto",
    )
    ax2_map.set_title(
        r"c. $\Delta UI^{LA}$",
        fontsize=14,
        fontweight="normal",
        loc="left",
        x=-0.05,
        y=1.05,
        pad=5,
    )

    pos_map2 = ax2_map.get_position()
    cbar_ax = fig.add_axes(
        [pos_map2.x0 + 0.12, pos_map2.y0 - 0.06, pos_map2.width * 0.6, 0.02]
    )
    cbar = plt.colorbar(
        mesh2,
        shrink=0.93,
        orientation="horizontal",
        extend="both",
        pad=0.035,
        aspect=30,
        cax=cbar_ax,
    )
    cbar.set_label(r"$\Delta$UI", fontsize=12)

    # Panel d: La Niña vs. Neutral bar chart
    ax2_bar = fig.add_subplot(gs[1, 1])
    fig.canvas.draw()
    pos_map2 = ax2_map.get_position()
    pos_bar2 = ax2_bar.get_position()
    ax2_bar.set_position(
        [pos_bar2.x0, pos_bar2.y0 + 0.04, pos_bar2.width, pos_map2.height]
    )

    ax2_bar.bar(
        x + 0.5 * width,
        la_day_means,
        width,
        yerr=la_day_stds,
        capsize=4,
        color="#de9e83",
        alpha=0.85,
        edgecolor="black",
        linewidth=0.8,
        label=r"$UI^{LA}_{dt} - UI^{NE}_{dt}$",
        error_kw={"elinewidth": 1.0, "ecolor": "black"},
    )
    ax2_bar.bar(
        x + 1.5 * width,
        la_night_means,
        width,
        yerr=la_night_stds,
        capsize=4,
        color="#293F81",
        alpha=0.85,
        edgecolor="black",
        linewidth=0.8,
        label=r"$UI^{LA}_{nt} - UI^{NE}_{nt}$",
        error_kw={"elinewidth": 1.0, "ecolor": "black"},
    )

    ax2_bar.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax2_bar.set_xticks(x + 1.0 * width)
    ax2_bar.set_xticklabels(
        all_labels, fontsize=11, fontweight="normal", rotation=45
    )
    ax2_bar.set_ylabel(r"$UI^{LA}$ vs. $UI^{NE}$ (%)", fontsize=12)
    ax2_bar.set_title(
        r"d. $UI^{LA}$ vs. $UI^{NE}$",
        fontsize=14,
        fontweight="normal",
        loc="left",
        x=-0.15,
    )
    ax2_bar.legend(frameon=False, fontsize=10, loc="upper right")
    ax2_bar.grid(axis="y", linestyle=":", alpha=0.6)

    # Format map ticks and labels
    ax1_map.set_xticks([-120, 0, 120], crs=proj)
    ax1_map.set_yticks(np.arange(region_plot[-2], region_plot[-1] + 1, 30), crs=proj)
    ax1_map.yaxis.set_major_formatter(LatitudeFormatter())
    ax1_map.tick_params(axis="y", labelsize=12)
    ax1_map.set_xlabel("")
    ax1_map.set_ylabel("")
    ax1_map.set_xticklabels([])

    ax2_map.set_xticks([-120, 0, 120], crs=proj)
    ax2_map.set_yticks(np.arange(region_plot[-2], region_plot[-1] + 1, 30), crs=proj)
    ax2_map.xaxis.set_major_formatter(LongitudeFormatter())
    ax2_map.yaxis.set_major_formatter(LatitudeFormatter())
    ax2_map.set_xlabel("")
    ax2_map.set_ylabel("")
    ax2_map.tick_params(axis="both", labelsize=12)

    # --------------------------------------------------------------------------
    # Panel e: Latitudinal Zonal Profiles
    # --------------------------------------------------------------------------
    ax_zonal = fig.add_axes(
        [pos_map2.x0, pos_map2.y0 - 0.42, pos_map2.width * 1.6, 0.3]
    )
    ax_zonal.set_title(
        "e. Latitude zones", fontsize=14, fontweight="normal", loc="left", x=-0.05
    )

    y_mins, y_maxs = [], []
    custom_lat_bins = [60, 40, 23.5, 0, -23.5, -40, -60]
    curves_config = [
        (map_el_dn_diff, "#D55E00", "#D55E00", r"$\Delta UI^{EL}$"),
        (map_la_dn_diff, "#0072B2", "#0072B2", r"$\Delta UI^{LA}$"),
        (map_ne_dn_diff, "#7F7F7F", "#7F7F7F", r"$\Delta UI^{NE}$"),
    ]

    for data_map, line_col, fill_col, lbl in curves_config:
        mi, ma = plot_zonal_profile(
            ax_zonal,
            data_map,
            lat,
            color=line_col,
            fill_color=fill_col,
            lat_bins=custom_lat_bins,
            label=lbl,
            show_hemisphere_means=False,
        )
        y_mins.append(mi)
        y_maxs.append(ma)

    g_min, g_max = min(y_mins), max(y_maxs)
    pad = (g_max - g_min) * 0.08
    ax_zonal.set_ylim(g_min - pad, g_max + pad)
    ax_zonal.axhline(0, color="gray", linewidth=0.8, linestyle="--")
    ax_zonal.set_yscale("symlog", linthresh=0.004)

    ax_zonal.set_xlabel("Latitude", fontsize=14, fontweight="normal", labelpad=5)
    ax_zonal.set_ylabel(r"$\Delta$UI", fontsize=14, fontweight="normal", labelpad=5)
    ax_zonal.legend(
        loc="upper right",
        ncols=2,
        frameon=True,
        facecolor="none",
        framealpha=0.85,
        fontsize=12,
        edgecolor="none",
    )
    # Save figure
    # plt.savefig(OUTPUT_FIG_PATH, format="png", dpi=600, bbox_inches="tight")
    print(f"Figure successfully saved to {OUTPUT_FIG_PATH}")
if __name__ == "__main__":
    main()

# %%
