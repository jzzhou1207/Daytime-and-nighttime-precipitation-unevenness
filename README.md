# Daytime-and-nighttime-precipitation-unevenness
This repository 被用于 提交至Geophysical Research Letters 期刊，title 为Increasing contributions of extremes to daytime and nighttime precipitation unevenness的manuscript的code.

./day_night_divide 用于计算逐格点的白天时间索引和夜间时间索引
./calculate_unevenness_index 用于计算逐格点的白天降水和夜间降水的relative entropy (RE)以及unevenness index (UI)
./spatial_pattern_fig1 用于绘制Spatial patterns of daytime and nighttime precipitation unevenness
./pearson_correlation_coefficient_fig2 用于绘制Pearson correlation coefficient between relative entropy (RE) and rainfall/rainfall_max (R/Rmax).
./region_fig3 用于绘制Regional daytime and nighttime precipitation unevenness.
./extreme_fig4 用于绘制Relative contribution of extreme events to precipitation unevenness

Data: The Integrated Multi-satellitE Retrievals (IMERG) for Global Precipitation Mission (GPM) data is from https://gpm.nasa.gov/. Climate reference regions are sources from https://www.ipcc-data.org/guidelines/pages/ar5_regions.html.
