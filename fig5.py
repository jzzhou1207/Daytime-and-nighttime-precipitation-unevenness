# %% [markdown]
# # Environmental Mechanisms of Diurnal Precipitation Asymmetry Across ENSO Phases (Figure 5)
# This script calculates and visualizes the spatial distributions and zonal profiles
# of daytime-nighttime differences in environmental variables (TCWV, CAPE, 
# Upward omega at 700 hPa and 850 hPa) during El Niño, La Niña, and Neutral years.

# %%
import os
import numpy as np
import xarray as xr
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
DATA_DIR = BASE_DIR / "data" / "fig5"
OUTPUT_DIR = Path("/")

# ==============================================================================
# 0. Path Configuration
# ==============================================================================

# Original data paths preserved under BASE_DIR
NC_FILE_EN = os.path.join(
    DATA_DIR, "ERA5_env_state_ElNino_yearly.nc"
)
NC_FILE_LA = os.path.join(
    DATA_DIR, "ERA5_env_state_LaNina_yearly.nc"
)
NC_FILE_NE = os.path.join(
    DATA_DIR, "ERA5_env_state_Neutral_yearly.nc"
)
OUTPUT_FIG_PATH = os.path.join(
    OUTPUT_DIR, "environment_mechanism_spatial_enso.png"
)


# ==============================================================================
# 1. Helper Functions
# ==============================================================================
def plot_zonal_profile(
    ax,
    data,
    lat,
    color="black",
    fill_color="gray",
    lat_bins=[60, 40, 23.5, 0, -23.5, -40, -60],
    label="",
    decimals=1,
    text_row=0,
    show_annot=True,
):
    """
    Calculate and plot zonal arithmetic mean profiles, 25th-75th percentile shading,
    and latitude-zone mean horizontal lines with top annotations.
    """
    if hasattr(data, "values"):
        val_array = np.array(data.values, copy=True)
    else:
        val_array = np.array(data, copy=True)

    # 1. Zonal arithmetic mean and interquartile range (25% - 75%)
    zonal_mean = np.nanmean(val_array, axis=1)
    zonal_q25 = np.nanpercentile(val_array, 25, axis=1)
    zonal_q75 = np.nanpercentile(val_array, 75, axis=1)

    # 2. Plot continuous zonal profile and shading
    ax.plot(
        lat,
        zonal_mean,
        color=color,
        linewidth=0.5,
        alpha=0.7,
        linestyle="-",
        label=label,
    )
    ax.fill_between(lat, zonal_q25, zonal_q75, alpha=0.06, color=fill_color)

    # 3. Calculate and plot arithmetic mean per custom latitude zone
    all_b_means = []
    for i in range(len(lat_bins) - 1):
        lat_high = lat_bins[i]
        lat_low = lat_bins[i + 1]

        idx = np.where(
            (lat >= min(lat_low, lat_high)) & (lat <= max(lat_low, lat_high))
        )[0]

        if len(idx) > 0:
            sub_data = val_array[idx, :]
            b_mean = float(np.nanmean(sub_data))
            all_b_means.append(b_mean)

            # Horizontal mean line for the latitude zone
            ax.hlines(
                y=b_mean,
                xmin=lat_high,
                xmax=lat_low,
                color=color,
                linewidth=1.5,
                zorder=4,
            )

            # Top 3-row mean value annotations per latitude zone
            if show_annot:
                x_center = (lat_high + lat_low) / 2.0
                y_pos = 0.96 - text_row * 0.06
                val_str = f"{b_mean:.{decimals}f}"

                ax.text(
                    x_center,
                    y_pos,
                    val_str,
                    color=color,
                    fontsize=8,
                    fontweight="bold",
                    ha="center",
                    va="top",
                    transform=ax.get_xaxis_transform(),
                    zorder=10,
                )

    # 4. Configure axes and latitude ticks (60°N to 60°S)
    ax.set_xlim(60, -60)
    ax.set_xticks(lat_bins)
    lat_labels = [
        f"{abs(deg)}°N" if deg > 0 else (f"{abs(deg)}°S" if deg < 0 else "0°")
        for deg in lat_bins
    ]
    ax.set_xticklabels(lat_labels, fontsize=10)

    for b in lat_bins:
        ax.axvline(x=b, color="gray", linestyle=":", alpha=0.3, linewidth=0.8)

    ax.grid(True, linestyle=":", alpha=0.3)

    y_min = min(all_b_means) if all_b_means else 0
    y_max = max(all_b_means) if all_b_means else 0
    return y_min, y_max


# ==============================================================================
# 2. Data Loading & Variable Configuration
# ==============================================================================
ds_en = xr.open_dataset(NC_FILE_EN)
ds_la = xr.open_dataset(NC_FILE_LA)
ds_ne = xr.open_dataset(NC_FILE_NE)

lon = ds_en["longitude"].values
lat = ds_en["latitude"].values

# Variable metadata (sign = -1.0 converts omega to upward vertical velocity)
var_info = {
    "TCWV": {
        "day": "baseline_tcwv_day",
        "night": "baseline_tcwv_night",
        "unit": r"\mathrm{kg}\cdot\mathrm{m}^{-2}",
        "title": "TCWV",
        "sign": 1.0,
        "cmap": "RdBu_r",
        "ylim": (-1.5, 2.5),
    },
    "CAPE": {
        "day": "baseline_cape_day",
        "night": "baseline_cape_night",
        "unit": r"\mathrm{J}\cdot\mathrm{kg}^{-1}",
        "title": "CAPE",
        "sign": 1.0,
        "cmap": "RdBu_r",
        "ylim": (-50.0, 200.0),
    },
    "VV700": {
        "day": "baseline_vv_day",
        "night": "baseline_vv_night",
        "unit": r"\mathrm{Pa}\cdot\mathrm{s}^{-1}",
        "title": r"Upward\ \omega (700 hPa)",
        "sign": -1.0,
        "cmap": "RdBu_r",
        "ylim": (-0.025, 0.075),
    },
    "VV850": {
        "day": "baseline_vv850_day",
        "night": "baseline_vv850_night",
        "unit": r"\mathrm{Pa}\cdot\mathrm{s}^{-1}",
        "title": r"Upward\ \omega (850 hPa)",
        "sign": -1.0,
        "cmap": "RdBu_r",
        "ylim": (-0.025, 0.075),
    },
}
var_order = ["TCWV", "CAPE", "VV700", "VV850"]

lat_bins = [60, 40, 23.5, 0, -23.5, -40, -60]
line_colors = {
    "El Niño": "#d73027",  # Red
    "La Niña": "#4575b4",  # Blue
    "Neutral": "#4d4d4d",  # Dark gray
}


# ==============================================================================
# 3. Figure Generation (4 Rows x 3 Columns)
# ==============================================================================
letters = [f"{chr(97 + i)}." for i in range(12)]
lon_ticks = [-120, 0, 120]
lat_ticks = [-60, -30, 0, 30, 60]

fig = plt.figure(figsize=(16, 12 / 22 * 16), dpi=120)
plt.subplots_adjust(
    wspace=0.25, hspace=0.35, left=0.05, right=0.95, top=0.94, bottom=0.05
)
gs = fig.add_gridspec(
    4,
    5,
    width_ratios=[1, 0.03, 1, 0.5, 1],
    wspace=0,
    hspace=0.35,
    left=0.05,
    right=0.95,
    top=0.94,
    bottom=0.05,
)

for row, var_key in enumerate(var_order):
    info = var_info[var_key]
    sign = info["sign"]

    # Calculate multi-year mean daytime-nighttime contrast (Day - Night)
    en_day_map = np.nanmean(ds_en[info["day"]].values * sign, axis=0)
    en_night_map = np.nanmean(ds_en[info["night"]].values * sign, axis=0)
    en_diurnal_map = en_day_map - en_night_map

    la_day_map = np.nanmean(ds_la[info["day"]].values * sign, axis=0)
    la_night_map = np.nanmean(ds_la[info["night"]].values * sign, axis=0)
    la_diurnal_map = la_day_map - la_night_map

    ne_day_map = np.nanmean(ds_ne[info["day"]].values * sign, axis=0)
    ne_night_map = np.nanmean(ds_ne[info["night"]].values * sign, axis=0)
    ne_diurnal_map = ne_day_map - ne_night_map

    # Symmetric colorbar range based on the 98th percentile
    vmax = np.nanpercentile(
        np.abs(np.concatenate([en_diurnal_map, la_diurnal_map])), 98
    )
    vmin = -vmax

    # ------------------ Column 1: El Niño Diurnal Contrast ------------------
    ax1_idx = row * 3
    ax1 = fig.add_subplot(gs[row, 0], projection=ccrs.PlateCarree())
    ax1.coastlines(resolution="110m", color="black", linewidth=0.8)
    ax1.set_extent([-180, 180, -60, 60], crs=ccrs.PlateCarree())
    im1 = ax1.pcolormesh(
        lon,
        lat,
        en_diurnal_map,
        transform=ccrs.PlateCarree(),
        cmap=info["cmap"],
        vmin=vmin,
        vmax=vmax,
    )
    ax1.set_title(
        f"{letters[ax1_idx]} $\Delta$$\mathrm{{{info['title']}}}$ (El Niño)",
        fontsize=12,
        fontweight="normal",
        loc="left",
    )

    # ------------------ Column 2: La Niña Diurnal Contrast ------------------
    ax2_idx = row * 3 + 1
    ax2 = fig.add_subplot(gs[row, 2], projection=ccrs.PlateCarree())
    ax2.coastlines(resolution="110m", color="black", linewidth=0.8)
    ax2.set_extent([-180, 180, -60, 60], crs=ccrs.PlateCarree())
    im2 = ax2.pcolormesh(
        lon,
        lat,
        la_diurnal_map,
        transform=ccrs.PlateCarree(),
        cmap=info["cmap"],
        vmin=vmin,
        vmax=vmax,
    )
    ax2.set_title(
        f"{letters[ax2_idx]} $\Delta$$\mathrm{{{info['title']}}}$ (La Niña)",
        fontsize=12,
        fontweight="normal",
        loc="left",
    )

    # Shared Vertical Colorbar for Columns 1 & 2
    pos = ax2.get_position()
    cbar_ax = fig.add_axes([0.58, pos.y0, 0.007, 0.16])
    cbar = fig.colorbar(im2, cax=cbar_ax, orientation="vertical", extend="both")
    cbar.set_label(
        f"${info['unit']}$",
        fontsize=10,
        rotation=0,
        loc="bottom",
        labelpad=-25,
        va="center",
    )

    # Map Ticks and Formatters
    ax1.set_xticks(lon_ticks, crs=ccrs.PlateCarree())
    ax1.set_yticks(lat_ticks, crs=ccrs.PlateCarree())
    ax1.xaxis.set_major_formatter(LongitudeFormatter())
    ax1.yaxis.set_major_formatter(LatitudeFormatter())
    ax1.tick_params(axis="both", direction="out", length=5, width=0.8)
    if row < 2:
        ax1.set_xticklabels([])

    ax2.set_xticks(lon_ticks, crs=ccrs.PlateCarree())
    ax2.set_yticks(lat_ticks, crs=ccrs.PlateCarree())
    ax2.xaxis.set_major_formatter(LongitudeFormatter())
    ax2.yaxis.set_major_formatter(LatitudeFormatter())
    ax2.tick_params(axis="both", direction="out", length=5, width=0.8)
    ax2.set_yticklabels([])
    if row != 3:
        ax2.set_xticklabels([])

    # ------------------ Column 3: Zonal Profile Distribution ------------------
    ax3_idx = row * 3 + 2
    ax3 = fig.add_subplot(gs[row, 4])
    ax3.set_box_aspect(120 / 360)

    y_mins, y_maxs = [], []
    curves_config = [
        (ne_diurnal_map, line_colors["Neutral"], line_colors["Neutral"], "Neutral"),
        (en_diurnal_map, line_colors["El Niño"], line_colors["El Niño"], "El Niño"),
        (la_diurnal_map, line_colors["La Niña"], line_colors["La Niña"], "La Niña"),
    ]
    is_vv = "VV" in var_key
    dec = 4 if is_vv else 2

    for i, (d, c, fc, lbl) in enumerate(curves_config):
        mi, ma = plot_zonal_profile(
            ax3,
            d,
            lat,
            color=c,
            fill_color=fc,
            lat_bins=lat_bins,
            label=lbl,
            decimals=dec,
            text_row=i,
            show_annot=True,
        )
        y_mins.append(mi)
        y_maxs.append(ma)

    if "ylim" in info and info["ylim"] is not None:
        ax3.set_ylim(info["ylim"])
    else:
        g_min, g_max = min(y_mins), max(y_maxs)
        pad = (g_max - g_min) * 0.1
        ax3.set_ylim(g_min - pad, g_max + pad)

    ax3.axhline(0, color="gray", linewidth=0.8, linestyle="--")

    if row == 3:
        lat_labels = [
            f"{abs(deg)}°N" if deg > 0 else (f"{abs(deg)}°S" if deg < 0 else "0°")
            for deg in lat_bins
        ]
        ax3.set_xticklabels(lat_labels, fontsize=10)
        ax3.set_xlabel("Latitude", fontsize=10)
    else:
        ax3.set_xticklabels([])
        ax3.set_xlabel("")

    ax3.set_ylabel(f"$\Delta$ ${info['title']}$\n(${info['unit']}$)", fontsize=10)
    ax3.set_title(
        f"{letters[ax3_idx]} Latitude Zones (${info['title']}$)",
        fontsize=12,
        fontweight="normal",
        loc="left",
    )

    if row == 0:
        ax3.legend(
            loc="upper right",
            fontsize=9,
            framealpha=0.8,
            frameon=False,
            bbox_to_anchor=(1.0, -0.1),
            ncol=3,
        )

plt.tight_layout()
# Save figure (uncomment to export)
# plt.savefig(OUTPUT_FIG_PATH, format="png", dpi=600, bbox_inches="tight")
# %%