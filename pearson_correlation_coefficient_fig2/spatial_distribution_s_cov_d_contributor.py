#%%
# -*- coding: utf-8 -*-
#代码用于对比RE和r/rmax对DSI的贡献
"""
Created on Sun Jan 28 16:07:50 2024

@author: 11434
"""

import netCDF4 as nc
import numpy as np
from matplotlib import pyplot as plt
import cartopy.crs as ccrs
#from osgeo import gdal
import cartopy.feature as cfeature
from scipy.stats import norm
import matplotlib as mpl
import cartopy.mpl.geoaxes
import glob
import os
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
import pandas as pd
from cartopy.mpl.ticker import LatitudeFormatter, LongitudeFormatter
import seaborn as sns
import scipy.stats as stats
from scipy.stats import theilslopes
##读取降水数据###

def calculate_annual_precipitation_mean(folder_path,file_prefix,light_var, dark_var):
    # 查找文件夹中的.nc文件
    file_pattern = os.path.join(folder_path, f'{file_prefix}*.nc')
    nc_files = glob.glob(file_pattern)
    nc_files = sorted(glob.glob(file_pattern))[:]  # 读取所有年份
    # 初始化空列表，用于存储白天和夜间降水数据
    all_day_data = []
    all_night_data = []
    
    # 循环读取所有文件
    for nc_file in nc_files:
        # 打开.nc文件
        with nc.Dataset(nc_file, 'r') as ds:
            # 获取白天和夜间降水数据
            day_data = ds.variables[light_var][:]
            day_data = np.squeeze(day_data)
            night_data = ds.variables[dark_var][:]
            night_data = np.squeeze(night_data)
            
            # 将数据添加到列表中
            all_day_data.append(day_data)
            all_night_data.append(night_data)
    
    # 将所有数据合并为一个大的数组
    all_day_data2 = np.stack(all_day_data, axis=0)
    all_night_data2 = np.stack(all_night_data, axis=0)
    
    # 计算白天和夜间降水的平均值
    daymean = np.nanmean(all_day_data2, axis=0)
    nightmean = np.nanmean(all_night_data2, axis=0)
    
    return daymean, nightmean

def calculate_annual_precipitation_yearly(folder_path,file_prefix,light_var, dark_var):
    # 查找文件夹中的.nc文件
    file_pattern = os.path.join(folder_path, f'{file_prefix}*.nc')
    nc_files = glob.glob(file_pattern)
    nc_files = sorted(glob.glob(file_pattern))[:]  # 读取所有年份
    # 初始化空列表，用于存储白天和夜间降水数据
    all_day_data = []
    all_night_data = []
    
    # 循环读取所有文件
    for nc_file in nc_files:
        # 打开.nc文件
        with nc.Dataset(nc_file, 'r') as ds:
            # 获取白天和夜间降水数据
            day_data = ds.variables[light_var][:]
            day_data = np.squeeze(day_data)
            night_data = ds.variables[dark_var][:]
            night_data = np.squeeze(night_data)
            
            # 将数据添加到列表中
            all_day_data.append(day_data)
            all_night_data.append(night_data)
    
    # 将所有数据合并为一个大的数组
    all_day_data2 = np.stack(all_day_data, axis=0)
    all_night_data2 = np.stack(all_night_data, axis=0)
    
    
    return all_day_data2, all_night_data2

#计算不均匀性逐年趋势
years = np.arange(2001,2023,1)
def read_year_extreme(folder_path,file_prefix,day_var,night_var,number):
    file_pattern = os.path.join(folder_path, f'{file_prefix}*.nc')
    nc_files = sorted(glob.glob(file_pattern))[:]  # 读取所有年份
    
    yearly_day_data = []
    yearly_night_data = []
    yearly_diff_data = []
    #years = []
    
    for nc_file in nc_files:
        with nc.Dataset(nc_file, 'r') as ds:
            # 从文件名提取年份 (假设文件名包含年份)
            #year = int(os.path.basename(nc_file).split('_')[-1].split('.')[0])
            #years.append(year)
            
            # 读取白天和夜间降水数据
            day_data = ds.variables[day_var][:].flatten() / number
            night_data = ds.variables[night_var][:].flatten() /number 
            diff_data = day_data - night_data
            yearly_day_data.append(day_data)
            yearly_night_data.append(night_data)
            yearly_diff_data.append(diff_data)
    day_df = pd.DataFrame(np.column_stack(yearly_day_data), columns=[f'Day_{year}' for year in years])
    night_df = pd.DataFrame(np.column_stack(yearly_night_data), columns=[f'Night_{year}' for year in years])
    return day_df, night_df

#%%
nc_precmean = nc.Dataset("./data/fig1/annual_pre/annual_precipitation_2001.nc")
lon=nc_precmean.variables['longitude'][:]
lat=nc_precmean.variables['latitude'][:]
nc_precmean.close()

#daymax =  5748.13623046875
daymax = 7959.97021484375
nightmax = 7959.97021484375

with nc.Dataset("./data/fig1/years_01_22.nc", 'r') as ds:
    # 获取白天和夜间降水数据
    dayprepyearly = ds.variables["dayprec"][:]
    nightprepyearly = ds.variables["nightprec"][:]

with nc.Dataset("./data/landmask_0.1deg.nc", 'r') as ds:
    # 获取白天和夜间降水数据
    mask = ds.variables["mask"][:]


folder_path = './data/fig1/D_index_light/'  # 传入你想读取的文件夹路径
file_prefix = 'concatenated_daily_precipitation_'  # 文件名前缀
light_var = 'D_daily'  # 白天降水的变量名
dark_var = 'D_monthly'  # 夜间降水的变量名
daytime_re_daily_yearly, day_re_monthly_yearly = calculate_annual_precipitation_yearly(folder_path, file_prefix, light_var, dark_var)

folder_path = './data/fig1/D_index_night/'  # 传入你想读取的文件夹路径
file_prefix = 'concatenated_daily_precipitation_'  # 文件名前缀
light_var = 'D_daily'  # 白天降水的变量名
dark_var = 'D_monthly'  # 夜间降水的变量名
nighttime_re_daily_yearly, night_re_monthly_yearly = calculate_annual_precipitation_yearly(folder_path, file_prefix, light_var, dark_var)


folder_path = './data/fig1/dsi_nightmax/'  # 传入你想读取的文件夹路径
file_prefix = 'concatenated_daily_precipitation_'  # 文件名前缀
light_var = 'S_daily'  # 白天降水的变量名
dark_var = 'S_monthly'  # 夜间降水的变量名
daytime_dsi_daily_yearly, day_dsi_monthly_yearly = calculate_annual_precipitation_yearly(folder_path, file_prefix, light_var, dark_var)

folder_path = './data/fig1/S_night_index/'  # 
file_prefix = 'concatenated_daily_precipitation_'  # 文件名前缀
light_var = 'S_daily'  # 白天降水的变量名
dark_var = 'S_monthly'  # 夜间降水的变量名
nighttime_dsi_daily_yearly, night_dsi_monthly_yearly = calculate_annual_precipitation_yearly(folder_path, file_prefix, light_var, dark_var)

Rday_contributor = np.nanmean(dayprepyearly, axis=0) / daymax # 
Rnight_contributor = np.nanmean(nightprepyearly, axis=0) / nightmax
Rday_contributor = Rday_contributor * mask
Rnight_contributor = Rnight_contributor * mask
dayprepyearly = dayprepyearly * mask
nightprepyearly = nightprepyearly * mask

REday_contributor = np.nanmean(daytime_re_daily_yearly, axis=0)
REnight_contributor = np.nanmean(nighttime_re_daily_yearly, axis=0)
REday_contributor  = REday_contributor * mask 
REnight_contributor = REnight_contributor * mask
daytime_re_daily_yearly = daytime_re_daily_yearly * mask    
nighttime_re_daily_yearly = nighttime_re_daily_yearly * mask

DSIday = np.nanmean(daytime_dsi_daily_yearly, axis=0)
DSInight = np.nanmean(nighttime_dsi_daily_yearly, axis=0)
DSIday = DSIday * mask
DSInight = DSInight * mask
daytime_dsi_daily_yearly = daytime_dsi_daily_yearly * mask
nighttime_dsi_daily_yearly = nighttime_dsi_daily_yearly * mask

#%%
#计算相关系数：
from scipy.stats import pearsonr
import scipy.special
def vectorized_correlation(F_ts, G_ts):
    """
    使用向量化方法计算每个空间格点上两个时间序列的相关系数
    
    参数:
    F_ts, G_ts : numpy.ndarray (years, lat, lon)
    
    返回:
    corr_matrix : numpy.ndarray (lat, lon)
        相关系数矩阵
    p_value_matrix : numpy.ndarray (lat, lon)
        相关系数p值矩阵
    """
    # 获取维度信息
    n_years, n_lat, n_lon = F_ts.shape

    # 计算有效样本数
    valid_mask = ~np.isnan(F_ts) & ~np.isnan(G_ts)
    valid_count = np.sum(valid_mask, axis=0)

    # 初始化结果矩阵
    corr_matrix = np.full((n_lat, n_lon), np.nan)
    p_value_matrix = np.full((n_lat, n_lon), np.nan)
    
    # 计算时间序列的均值和标准差
    F_mean = np.nanmean(F_ts, axis=0)
    G_mean = np.nanmean(G_ts, axis=0)
    F_std = np.nanstd(F_ts, axis=0, ddof=1)
    G_std = np.nanstd(G_ts, axis=0, ddof=1)
    
    # 计算协方差
    F_diff = F_ts - F_mean[np.newaxis, :, :]
    G_diff = G_ts - G_mean[np.newaxis, :, :]
    cov_matrix = np.nansum(F_diff * G_diff, axis=0) / (n_years-1)
    with np.errstate(divide='ignore', invalid='ignore'):
        corr_matrix = cov_matrix / (F_std * G_std)
    corr_matrix = np.where(np.abs(corr_matrix) > 1, np.nan, corr_matrix)    
    # 计算相关系数
    df = valid_count - 2  # 自由度
    df = np.where(df > 0, df, 0)
    with np.errstate(divide='ignore', invalid='ignore'):
        # 更稳健的t统计量计算
        t_stat = np.zeros_like(corr_matrix)
        valid = (np.abs(corr_matrix) < 1) & (~np.isnan(corr_matrix))
        t_stat[valid] = corr_matrix[valid] * np.sqrt(df[valid] / (1 - corr_matrix[valid]**2))
        t_stat[corr_matrix == 1] = np.inf   # 完全正相关
        t_stat[corr_matrix == -1] = -np.inf  # 完全负相关
    
    # 正确的p值计算（使用t分布的生存函数）
    p = 2 * scipy.special.stdtr(df, -np.abs(t_stat))
    p_value_matrix = np.where(valid, p, np.nan)
    
    return corr_matrix, p_value_matrix

corr_day, p_value_day = vectorized_correlation(
    F_ts=daytime_re_daily_yearly,  # RE时间序列
    G_ts=dayprepyearly / daymax    # R/Rmax时间序列
)
corr_day = corr_day * mask
masked_corr_day = corr_day.copy().astype(float)
masked_corr_day[p_value_day >= 0.05] = np.nan

total_valid_points = np.sum(~np.isnan(mask))
positive_points = np.sum(masked_corr_day > 0)
negative_points = np.sum(masked_corr_day < 0)
# 4. 计算比例（占总有效格点的比例）
positive_ratio = positive_points / total_valid_points
negative_ratio = negative_points / total_valid_points

# 计算每个格点的夜间相关系数
corr_night, p_value_night = vectorized_correlation(
    F_ts=nighttime_re_daily_yearly,
    G_ts=nightprepyearly / nightmax
)
corr_night = corr_night * mask
masked_corr_night = corr_night.copy().astype(float)
masked_corr_night[p_value_night >= 0.05] = np.nan

total_valid_points = np.sum(~np.isnan(mask))
positive_points = np.sum(masked_corr_night > 0)
negative_points = np.sum(masked_corr_night < 0)
# 4. 计算比例（占总有效格点的比例）
positive_ratio = positive_points / total_valid_points
negative_ratio = negative_points / total_valid_points

#%% 处理各个部分的占比
from sklearn.preprocessing import StandardScaler


def create_normalized_df(data_array, prefix, years):
    """创建DataFrame并可选归一化"""
    df = pd.DataFrame(
        data_array.reshape(len(years),-1).T,
        columns=[f'{prefix}_{year}' for year in years]
    )#.dropna()
    
    return df

# 参数设置
years = range(2001, 2023)  # 假设years是2001-2022
scaler = StandardScaler()
#mask pvalue 大于0.05
#mask_pday = p_value_day >= 0.05
#mask_pnight = p_value_night >= 0.05

daytime_re_daily_yearly_masked = daytime_re_daily_yearly.copy()
#daytime_re_daily_yearly_masked[:,mask_pday] = np.nan

nighttime_re_daily_yearly_masked = nighttime_re_daily_yearly.copy()
#nighttime_re_daily_yearly_masked[:,mask_pnight] = np.nan

dayprepyearly_masked = dayprepyearly.copy()
#dayprepyearly_masked[:,mask_pday] = np.nan

nightprepyearly_masked = nightprepyearly.copy()
#nightprepyearly_masked[:,mask_pnight] = np.nan

daytime_dsi_daily_yearly_masked = daytime_dsi_daily_yearly.copy()
#daytime_dsi_daily_yearly_masked[:,mask_pday] = np.nan

nighttime_dsi_daily_yearly_masked = nighttime_dsi_daily_yearly.copy()
#nighttime_dsi_daily_yearly_masked[:,mask_pnight] = np.nan

# 批量处理所有数据集
datasets = {
    'day_re': daytime_re_daily_yearly_masked,
    'night_re': nighttime_re_daily_yearly_masked,
    'day_r': dayprepyearly_masked/daymax,
    'night_r': nightprepyearly_masked/nightmax,
    'day_dsi': daytime_dsi_daily_yearly_masked,
    'night_dsi': nighttime_dsi_daily_yearly_masked
}

# 生成所有DataFrame
result_dfs = {}
for name, data in datasets.items():
    prefix = name.split('_')[0].capitalize()  # 提取Day/Night前缀
    result_dfs[name] = create_normalized_df(data, prefix, years)

# 计算均值
means = {f'mean_{name}': df.mean(skipna=True) for name, df in result_dfs.items()}

# 提取特定均值并归一化
years = np.arange(2001, 2023)  # 2001-2022
# 创建合并DataFrame
combined_df_day = pd.DataFrame({
    'Year': years,
    'Day_RE': means['mean_day_re'].values,
    'Day_R': means['mean_day_r'].values,
    'Day_DSI': means['mean_day_dsi'].values
})
#增加趋势分析
RE_day = theilslopes(combined_df_day['Day_RE'], combined_df_day['Year'],  alpha=0.95)
R_day = theilslopes(combined_df_day['Day_R'], combined_df_day['Year'], alpha=0.95)
DSI_day = theilslopes(combined_df_day['Day_DSI'], combined_df_day['Year'], alpha=0.95)

combined_df_day[['Day_RE_norm', 'Day_R_norm', 'Day_DSI_norm']] = scaler.fit_transform(
    combined_df_day[['Day_RE', 'Day_R', 'Day_DSI']])

combined_df_night = pd.DataFrame({
    'Year': years,
    'Night_RE': means['mean_night_re'].values,
    'Night_R': means['mean_night_r'].values,
    'Night_DSI': means['mean_night_dsi'].values
})
RE_night = theilslopes(combined_df_night['Night_RE'], combined_df_night['Year'],  alpha=0.95)
R_night = theilslopes(combined_df_night['Night_R'], combined_df_night['Year'], alpha=0.95)
DSI_night = theilslopes(combined_df_night['Night_DSI'], combined_df_night['Year'], alpha=0.95)

combined_df_night[['Night_RE_norm', 'Night_R_norm', 'Night_DSI_norm']] = scaler.fit_transform(
    combined_df_night[['Night_RE', 'Night_R', 'Night_DSI']])



#%%
#prec14_ratio=np.log10(prec14_ratio.data)
size1 = 22
fontdict = {'weight': 'bold','size':size1,'family':'SimHei'}
mpl.rcParams.update(
    {
        'text.usetex': False,                  # 不使用 LaTeX 渲染
        #'font.family': 'sans-serif',           # 设置字体为 sans-serif
        'font.sans-serif': ['Arial'],          # 指定 sans-serif 字体（如 Arial）
        'mathtext.fontset': 'stix',            # 数学字体设置为 stix
        'font.size': 20                    # 设置全局字体大小
    }
)

proj= ccrs.PlateCarree()
# 定义颜色和 colormap
colors1 = [
    '#ffffff', '#f7fcf0','#e1f3db','#cdebc5',
    '#aaddb5','#7fccc4','#53b3d3',
    '#318cbe','#0f68ac','#0f4081','#07203e'
]
colors2 = ['#2066ab',
           '#4292c2',
           '#91c4dd','#d0e4ef',
           "#ffffff",'#f5e7c2','#dec17d',
           '#be802d','#8b5009'#,'#532f04'
]
cmap = LinearSegmentedColormap.from_list('custom_cmap', colors1)
cmap2 = LinearSegmentedColormap.from_list('custom_cmap', colors2)
proj= ccrs.PlateCarree()
region = [-180,180,-60,60]

# **定义不同的颜色映射**

boundaries = np.arange(-0.45, 0.46, 0.1)  # 适用于后 2 个子图
norm = BoundaryNorm(boundaries, cmap2.N, extend='both')

def plot_geospatial_data(ax, lon, lat, data, 
                         cmap='viridis', norm=None,
                         region=[-180, 180, -60, 60],
                         land_color='grey', land_alpha=0.4,
                         coastline_width=0.8):
        pcm = ax.pcolormesh(lon, lat, data, 
                       cmap=cmap, norm=norm,
                       transform=ccrs.PlateCarree())
        # 添加地理特征
        ax.add_feature(cfeature.LAND, color=land_color, alpha=land_alpha, 
                    edgecolor=None,linewidth=0.1)       
        # 设置地图属性
        ax.set_extent(region, crs=ccrs.PlateCarree())
        ax.coastlines(linewidth=coastline_width) 
        return pcm

def add_significance_dots(ax, lon, lat, p_mask, stride=10, 
                         dot_color='black', dot_size=1.5, dot_alpha=0.6):
    """
    在显著区域添加点状标记
    
    参数:
    ax: 目标坐标轴
    lon, lat: 经纬度网格 (1D 或 2D)
    p_mask: 显著性布尔掩码 (True表示显著)
    stride: 点密度控制 (越大点越稀疏)
    dot_*: 点样式控制参数
    """
    # 确保经纬度为二维网格
    if len(lon.shape) == 1:
        lon, lat = np.meshgrid(lon, lat)
    
    # 应用步长抽样
    sampled_mask = p_mask[::stride, ::stride]
    sampled_lon = lon[::stride, ::stride]
    sampled_lat = lat[::stride, ::stride]
    
    # 绘制显著点
    ax.scatter(sampled_lon[sampled_mask], 
               sampled_lat[sampled_mask],
               color=dot_color, 
               s=dot_size,
               alpha=dot_alpha,
               transform=ccrs.PlateCarree())


#%%
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), subplot_kw={"projection": ccrs.PlateCarree()})
region = [-180, 180, -60, 60]

for ax in [ax1, ax2]:
    ax.set_extent([-180, 180, -60, 60], crs=ccrs.PlateCarree())
    ax.coastlines(linewidth=0.5)
pos2 = ax1.get_position()

#此处绘制全球序列时候，适当延长ax1_day和ax2_night的宽度pos2.width/1.4 和 pos2.width/2
ax1_day = fig.add_axes([pos2.x1+0.08, pos2.y0 , pos2.width/1.4, pos2.height ])

pos3 = ax2.get_position()
ax2_night = fig.add_axes([pos3.x1+0.08, pos3.y0 , pos3.width/1.4, pos3.height ])

pcm1 = plot_geospatial_data(ax1, lon, lat, corr_day[:,:]*mask[:,:], 
                          cmap=cmap2, norm=norm,
                          land_color='lightgray',
                          land_alpha=0.6)
pcm2 = plot_geospatial_data(ax2, lon, lat, corr_night[:,:]*mask[:,:], 
                          cmap=cmap2, norm=norm,
                          land_color='lightgray',
                          land_alpha=0.6)
mask_sig_day = p_value_day < 0.05
mask_sig_night = p_value_night < 0.05
add_significance_dots(ax1, lon, lat, mask_sig_day, stride=20)
add_significance_dots(ax2, lon, lat, mask_sig_night, stride=20)

ax_bar = fig.add_axes([pos3.x0, pos3.y0-0.08 , pos3.width, 0.02 ])
b=plt.colorbar(pcm1,shrink=0.93,orientation='horizontal',extend='both',
               pad=0.035,aspect=30,cax = ax_bar)
# 设置刻度线朝内
ticks = np.arange(-0.45, 0.46, 0.1) # 生成刻度
b.set_ticks(ticks)  # 设置刻度位置
b.set_ticklabels([f'{t:.2f}' for t in ticks], fontsize=18,rotation=45)  # 设置刻度标签
b.ax.tick_params(direction='in', size=3.5, width=1.5)  # size=刻度线长度, width=刻度线宽度
minor_ticks = np.arange(-0.55, 0.56, 0.1) # 包括间隔 50 的刻度
b.ax.tick_params(which='minor', direction='in', size=3, width=0.5)  # 调整次刻度线样式
b.outline.set_edgecolor('black')  # 设置边框颜色
b.outline.set_linewidth(1)  # 设置边框线宽
b.set_label(r'$r$', fontsize=24, rotation=0)

ax1.set_xticks([-120,0,120], crs = proj)
ax1.set_yticks(np.arange(region[-2], region[-1] + 1, 30), crs = proj)
ax1.yaxis.set_major_formatter(LatitudeFormatter())
ax1.tick_params(axis='y', labelsize=20)  # 设置字体大小
ax1.set_xlabel(""); ax1.set_ylabel("")
ax1.set_xticklabels([])

ax2.set_xticks([-120,0,120], crs = proj)
ax2.set_yticks(np.arange(region[-2], region[-1] + 1, 30), crs = proj)
ax2.yaxis.set_major_formatter(LatitudeFormatter())
ax2.xaxis.set_major_formatter(LongitudeFormatter())
ax2.set_xlabel(""); ax2.set_ylabel("")
#ax2.set_yticklabels([]);ax2.set_xticklabels([]) 
ax1_day.axhline(y=0, color='gray', linestyle='-', linewidth=1) 
ax2_night.axhline(y=0, color='gray', linestyle='-', linewidth=1) 

scatter_plot = sns.lineplot(
    x='Year',
    y='Day_RE_norm',
    data=combined_df_day,
    color="#ACD2C7",                        # 线条颜色
    marker="o",                         # 数据点标记形状
    markersize=6,                         # 标记大小
    linewidth=1.5,linestyle="--",                        # 线条宽度
    ax=ax1_day                          # 指定绘制到哪个子图轴上
)
sns.regplot(
    x='Year', y='Day_RE_norm',
    data=combined_df_day,
    scatter=False,  # 不画散点
    fit_reg=True,
    line_kws={'color': '#ACD2C7', 'linewidth': 2},
    ax=ax1_day
)
scatter_plot = sns.lineplot(
    x='Year',
    y='Day_R_norm',
    data=combined_df_day,
    color="#94B5D8",                        # 线条颜色
    marker="o",                         # 数据点标记形状
    markersize=6,                        # 标记大小
    linewidth=1.5,linestyle="--",                        # 线条宽度
    ax=ax1_day                          # 指定绘制到哪个子图轴上
)
sns.regplot(
    x='Year', y='Day_R_norm',
    data=combined_df_day,
    scatter=False,  # 不画散点
    fit_reg=True,
    line_kws={'color': '#94B5D8', 'linewidth': 2},
    ax=ax1_day
)

scatter_plot = sns.lineplot(
    x='Year',
    y='Day_DSI_norm',
    data=combined_df_day,
    color="#D57B70",                        # 线条颜色
    marker="o",                         # 数据点标记形状
    markersize=6,                      # 标记大小
    linewidth=1.5,linestyle="--",                        # 线条宽度
    ax=ax1_day                          # 指定绘制到哪个子图轴上
)
sns.regplot(
    x='Year', y='Day_DSI_norm',
    data=combined_df_day,
    scatter=False,  # 不画散点
    fit_reg=True,
    line_kws={'color': '#D57B70', 'linewidth': 2},
    ax=ax1_day
)

ax1_day.set_xlabel(""); ax1_day.set_ylabel("Z-scores")
ax1_day.set_xticklabels([])

scatter_plot = sns.lineplot(
    x='Year',
    y='Night_RE_norm',
    data=combined_df_night,
    color="#ACD2C7",                        # 线条颜色
    marker="o",                         # 数据点标记形状
    markersize=6,                         # 标记大小
    linewidth=1.5,linestyle="--",               # 线条宽度
    ax=ax2_night                          # 指定绘制到哪个子图轴上
)
sns.regplot(
    x='Year', y='Night_RE_norm',
    data=combined_df_night,
    scatter=False,  # 不画散点
    fit_reg=True,
    line_kws={'color': '#ACD2C7', 'linewidth': 2},
    ax=ax2_night
)


scatter_plot = sns.lineplot(
    x='Year',
    y='Night_R_norm',
    data=combined_df_night,
    color="#94B5D8",                        # 线条颜色
    marker="o",                         # 数据点标记形状
    markersize=6,                         # 标记大小
    linewidth=1.5,linestyle="--",               # 线条宽度
    ax=ax2_night                          # 指定绘制到哪个子图轴上
)
sns.regplot(
    x='Year', y='Night_R_norm',
    data=combined_df_night,
    scatter=False,  # 不画散点
    fit_reg=True,
    line_kws={'color': '#94B5D8', 'linewidth': 2},
    ax=ax2_night
)

scatter_plot = sns.lineplot(
    x='Year',
    y='Night_DSI_norm',
    data=combined_df_night,
    color="#D57B70",                        # 线条颜色
    marker="o",                         # 数据点标记形状
    markersize=6,                         # 标记大小
    linewidth=1.5,linestyle="--",               # 线条宽度
    ax=ax2_night                          # 指定绘制到哪个子图轴上
)
sns.regplot(
    x='Year', y='Night_DSI_norm',
    data=combined_df_night,
    scatter=False,  # 不画散点
    fit_reg=True,
    line_kws={'color': '#D57B70', 'linewidth': 2},
    ax=ax2_night
)
ax2_night.set_xlabel("Years"); ax2_night.set_ylabel("Z-scores")

left = 0.02
top = 1.09
ax1.text(left, top, 'a ',
        horizontalalignment='center',
        verticalalignment='center',
        rotation=0,
        size=24,
        weight="bold", 
        transform=ax1.transAxes,clip_on = False) 

ax1_day.text(left, top, 'b ',
        horizontalalignment='center',
        verticalalignment='center',
        rotation=0,
        size=24,
        weight="bold", 
        transform=ax1_day.transAxes,clip_on = False) 
ax2.text(left, top, 'c ',
        horizontalalignment='center',
        verticalalignment='center',
        rotation=0,
        size=24,
        weight="bold", 
        transform=ax2.transAxes,clip_on = False) 
ax2_night.text(left, top, 'd ',
        horizontalalignment='center',
        verticalalignment='center',
        rotation=0,
        size=24,
        weight="bold", 
        transform=ax2_night.transAxes,clip_on = False) 
plt.savefig('./pearson_correlation_coefficient_fig2/dsi_re_r_cov_contributor_rmna_spatial_significant.png', format='png',dpi=600,bbox_inches='tight')
# %%
