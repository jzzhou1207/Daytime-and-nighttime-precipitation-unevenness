# %% [markdown]
# # Causal Mediation Analysis of Daytime and Nighttime UI Across ENSO Phases (Figure 6)
# This script visualizes the point estimates and 95% confidence intervals (CIs) 
# of Total Effects (TEs), Average Direct Effects (ADEs), and indirect environmental 
# pathways (CAPE, TCWV, and vertical velocity ω) for daytime and nighttime 
# precipitation unevenness index (UI) during El Niño and La Niña phases.

# %%
import os
import numpy as np
import matplotlib.pyplot as plt

# ==============================================================================
# 0. Path & Global Styling Configuration
# ==============================================================================
BASE_DIR = "/data1"
OUTPUT_FIG_PATH = os.path.join(
    BASE_DIR, "jzzhou/precipitation/season/mechanism/code/enso/enso_mediation_effects_fig6.png"
)

plt.rcParams["font.sans-serif"] = ["Arial", "Helvetica", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["pdf.fonttype"] = 42  # Ensure editable text when exporting to PDF/EPS
plt.rcParams["ps.fonttype"] = 42


# ==============================================================================
# 1. Mediation Effect Data & Color Schemes
# ==============================================================================
# Y-axis labels ordered from top (y=4) to bottom (y=0)
labels = ["TEs", "ADEs", "CAPE", "TCWV", r"$\omega$"]
y_pos = np.arange(len(labels))[::-1]

# Data format per row: [Point Estimate (Mean), 95% CI Lower Bound, 95% CI Upper Bound]
data = {
    "El Niño": {
        "Daytime UI": [
            [0.559, -0.327, 1.461],  # TEs
            [0.487, -0.151, 1.103],  # ADEs
            [0.007, -0.476, 0.273],  # CAPE
            [0.048, -0.793, 1.144],  # TCWV
            [0.016, -0.178, 0.384],  # ω
        ],
        "Nighttime UI": [
            [0.661, -0.233, 1.539],  # TEs
            [0.586, -0.038, 1.202],  # ADEs
            [0.043, -0.559, 0.459],  # CAPE
            [0.048, -0.823, 1.049],  # TCWV
            [-0.016, -0.201, 0.259], # ω
        ],
    },
    "La Niña": {
        "Daytime UI": [
            [0.840, -0.113, 1.992],  # TEs
            [-0.069, -0.883, 0.658], # ADEs
            [0.006, -0.511, 0.985],  # CAPE
            [0.593, -0.587, 1.467],  # TCWV
            [0.310, -0.655, 1.580],  # ω
        ],
        "Nighttime UI": [
            [0.475, -0.453, 1.595],  # TEs
            [-0.095, -0.838, 1.185], # ADEs
            [-0.018, -0.752, 1.149], # CAPE
            [0.563, -0.585, 1.578],  # TCWV
            [0.025, -1.086, 0.971],  # ω
        ],
    },
}

# Warm palette for El Niño, cool palette for La Niña
colors_el = {"Daytime UI": "#F39B7F", "Nighttime UI": "#C0392B"}
colors_la = {"Daytime UI": "#4DBBD5", "Nighttime UI": "#1F618D"}


# ==============================================================================
# 2. Figure Generation (Figure 6)
# ==============================================================================
fig, axes = plt.subplots(1, 2, figsize=(10.5, 5.2), sharey=True, dpi=300)
plt.subplots_adjust(wspace=0.10)

offset = 0.14  # Vertical offset between daytime and nighttime markers

panels = [
    ("El Niño", axes[0], colors_el, "a. El Niño"),
    ("La Niña", axes[1], colors_la, "b. La Niña"),
]

for phase, ax, colors, title in panels:
    # 1. Alternating horizontal background bands
    for y in y_pos:
        if y % 2 == 1:
            ax.axhspan(y - 0.5, y + 0.5, color="#F5F7FA", zorder=0)

    # 2. Zero-effect vertical reference line (x = 0)
    ax.axvline(0, color="#555555", linestyle="--", linewidth=1.2, zorder=1, alpha=0.8)

    # 3. Horizontal divider between Total/Direct effects and Indirect pathways
    ax.axhline(2.5, color="#CCCCCC", linestyle=":", linewidth=1.1, zorder=1)

    # 4. Plot 95% confidence intervals and point estimates
    for period, shift, marker in [("Daytime UI", offset, "o"), ("Nighttime UI", -offset, "s")]:
        vals = np.array(data[phase][period])
        means = vals[:, 0]
        lows = vals[:, 1]
        highs = vals[:, 2]

        xerr_low = means - lows
        xerr_high = highs - means

        ax.errorbar(
            means,
            y_pos + shift,
            xerr=[xerr_low, xerr_high],
            fmt="none",
            ecolor=colors[period],
            elinewidth=2.2,
            capsize=4,
            capthick=1.5,
            zorder=2,
        )

        ax.scatter(
            means,
            y_pos + shift,
            color=colors[period],
            marker=marker,
            s=75,
            edgecolors="white",
            linewidths=0.9,
            label=period,
            zorder=3,
        )

    # 5. Axis limits, labels, and spine formatting
    ax.set_xlim(-1.35, 2.25)
    ax.set_ylim(-0.55, 4.55)
    ax.set_xlabel("Effect Size (95% CI)", fontsize=11.5, fontweight="bold", labelpad=8)
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold", pad=12)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(1.1)
    ax.spines["bottom"].set_linewidth(1.1)
    ax.spines["left"].set_color("#333333")
    ax.spines["bottom"].set_color("#333333")

    ax.xaxis.grid(True, linestyle=":", alpha=0.4, color="#AAAAAA", zorder=0)
    ax.tick_params(axis="x", labelsize=10.5, direction="out", length=4, width=1.1)

    ax.legend(
        loc="lower right",
        frameon=False,
        fontsize=10,
        borderpad=0.5,
        handletextpad=0.4,
    )

# Y-axis tick formatting
axes[0].set_yticks(y_pos)
axes[0].set_yticklabels(labels, fontsize=11.5, fontweight="bold", color="#222222")
axes[0].tick_params(axis="y", length=0, pad=8)
axes[1].tick_params(axis="y", length=4, direction="in", color="#888888")

plt.tight_layout()
# Save figure (uncomment to export)
# plt.savefig(OUTPUT_FIG_PATH, format="png", dpi=600, bbox_inches="tight")
# %%