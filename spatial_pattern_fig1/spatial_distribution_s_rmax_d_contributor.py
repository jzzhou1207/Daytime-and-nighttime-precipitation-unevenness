#%%
# -*- coding: utf-8 -*-

"""
Created on Sun Jan 28 16:07:50 2024

@author: 11434
"""

import netCDF4 as nc
import numpy as np
from matplotlib import pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib as mpl
import glob
import os
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
import pandas as pd
from cartopy.mpl.ticker import LatitudeFormatter, LongitudeFormatter
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
folder_path = './data/fig1/annual_pre/'  # 传入你想读取的文件夹路径
file_prefix = 'annual_precipitation_'  # 文件名前缀
light_var = 'annualLightPrecipitation'  # 白天降水的变量名
dark_var = 'annualDarkPrecipitation'  # 夜间降水的变量名
dayprepmean, nightprepmean = calculate_annual_precipitation_mean(folder_path, file_prefix, light_var, dark_var)
mask = np.where(np.isnan(dayprepmean), dayprepmean, 1)

daymax =  7959.97021484375 #与夜间使用统一标准5748.13623046875
nightmax = 7959.97021484375

with nc.Dataset("./data/fig1/years_01_22.nc", 'r') as ds:
    # 获取白天和夜间降水数据
    dayprepyearly = ds.variables["dayprec"][:]
    nightprepyearly = ds.variables["nightprec"][:]


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

folder_path = './data/fig1/S_night_index/'  # 传入你想读取的文件夹路径
file_prefix = 'concatenated_daily_precipitation_'  # 文件名前缀
light_var = 'S_daily'  # 白天降水的变量名
dark_var = 'S_monthly'  # 夜间降水的变量名
nighttime_dsi_daily_yearly, night_dsi_monthly_yearly = calculate_annual_precipitation_yearly(folder_path, file_prefix, light_var, dark_var)

Rday_contributor = np.nanmean(dayprepyearly, axis=0) / daymax # in point [0,700,2026]
Rnight_contributor = np.nanmean(nightprepyearly, axis=0) / nightmax

REday_contributor = np.nanmean(daytime_re_daily_yearly, axis=0) * mask
REnight_contributor = np.nanmean(nighttime_re_daily_yearly, axis=0) * mask

DSIday = np.nanmean(daytime_dsi_daily_yearly, axis=0)
DSInight = np.nanmean(nighttime_dsi_daily_yearly, axis=0)


#%% 处理各个部分的占比
'''
pday1 = (REday_contributor * Rday_contributor) / DSIday * 100
pday_cov = cov_day / DSIday * 100
df_prd=pd.DataFrame({'pday1':pday1.flatten(),'pday_cov':pday_cov.flatten()})
df_prd=df_prd.dropna()
'''


#%%
#prec14_ratio=np.log10(prec14_ratio.data)
size1 = 20
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
colors2 = [
    (16/255, 70/255, 128/255),   # 深蓝
    (49/255, 124/255, 183/255),  # 蓝
    (109/255, 173/255, 209/255), # 浅蓝
    (182/255, 215/255, 232/255), # 非常浅蓝
    (233/255, 241/255, 244/255), # 白蓝
    (251/255, 227/255, 213/255), # 浅橙
    (246/255, 178/255, 147/255), # 橙
    (220/255, 109/255, 87/255),  # 深橙
    (183/255, 34/255, 48/255),   # 红
    (109/255, 1/255, 31/255)     # 深红
]
cmap = LinearSegmentedColormap.from_list('custom_cmap', colors1)
cmap2 = LinearSegmentedColormap.from_list('custom_cmap', colors2)
proj= ccrs.PlateCarree()
region = [-180,180,-60,60]

# **定义不同的颜色映射**
boundaries1 = np.arange(0, 0.51, 0.05)  # 适用于前 4 个子图
norm1 = BoundaryNorm(boundaries1, cmap.N, extend='max')

boundaries2 = np.arange(0, 8.1, 1.0)  # 适用于前 4 个子图
norm2 = BoundaryNorm(boundaries2, cmap.N, extend='max')

boundaries3 = np.arange(0, 0.21, 0.02)  # 适用于后 2 个子图
norm3 = BoundaryNorm(boundaries3, cmap2.N, extend='max')

boundaries4 = np.arange(-0.0005, 0.0005, 0.0001)  # 适用于后 2 个子图
norm4 = BoundaryNorm(boundaries4, cmap2.N, extend='max')

# 定义分段范围
#boundaries = np.arange(-200, 201, 50)  # 从 -100 到 100，步长为 50
#norm = BoundaryNorm(boundaries, cmap.N, extend='both')
#norm2=mpl.colors.Normalize(vmin=0,vmax=2)
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
#%%
fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(
    3, 2, figsize=(30, 16), subplot_kw={"projection": ccrs.PlateCarree()})
region = [-180, 180, -60, 60]
region = [-180, 180, -60, 60]
plt.subplots_adjust(wspace=0.05)
for ax in [ax1, ax2,ax3,ax4,ax5,ax6]:
    ax.set_extent([-180, 180, -60, 60], crs=ccrs.PlateCarree())
    ax.coastlines(linewidth=0.5)

pcm1 = plot_geospatial_data(ax1, lon, lat, Rday_contributor[:,:], 
                          cmap=cmap, norm=norm3,
                          land_color='lightgray',
                          land_alpha=0.6)
pcm2 = plot_geospatial_data(ax2, lon, lat, Rnight_contributor[:,:], 
                          cmap=cmap, norm=norm3,
                          land_color='lightgray',
                          land_alpha=0.6)

pcm3 = plot_geospatial_data(ax3, lon, lat, REday_contributor[:,:], 
                          cmap=cmap, norm=norm2,
                          land_color='lightgray',
                          land_alpha=0.6)
pcm4 = plot_geospatial_data(ax4, lon, lat, REnight_contributor[:,:], 
                          cmap=cmap, norm=norm2,
                          land_color='lightgray',
                          land_alpha=0.6)

pcm5 = plot_geospatial_data(ax5, lon, lat, DSIday[:,:], 
                          cmap=cmap, norm=norm1,
                          land_color='lightgray',
                          land_alpha=0.6)
pcm6 = plot_geospatial_data(ax6, lon, lat, DSInight[:,:], 
                          cmap=cmap, norm=norm1,
                          land_color='lightgray',
                          land_alpha=0.6)

# 计算数据的标准差和标准误差
std_val = np.nanstd(DSIday*mask, ddof=1)  # 样本标准差
n = np.sum(~np.isnan(DSIday*mask))        # 有效样本数

# 计算标准误 SEM = std / sqrt(n)
np.nanmean(DSIday*mask)
sem_value = std_val / np.sqrt(n)

#==========================添加图例 for individual
pos1 = ax2.get_position()
ax_bar1 = fig.add_axes([pos1.x1+0.015, pos1.y0 , 0.01, pos1.height ])
b=plt.colorbar(pcm1,shrink=0.93,orientation='vertical',extend='max',
               pad=0.035,aspect=30,cax = ax_bar1)
# 设置刻度线朝内
ticks = np.arange(0, 0.21, 0.04) # 生成刻度
b.set_ticks(ticks)  # 设置刻度位置
b.set_ticklabels([f'{t:.2f}' for t in ticks], fontsize=18)  # 设置刻度标签
b.ax.tick_params(direction='in', size=3.5, width=1.5)  # size=刻度线长度, width=刻度线宽度
minor_ticks = np.arange(0, 0.21, 0.02) # 包括间隔 50 的刻度
b.ax.tick_params(which='minor', direction='in', size=3, width=0.5)  # 调整次刻度线样式
b.outline.set_edgecolor('black')  # 设置边框颜色
b.outline.set_linewidth(1)  # 设置边框线宽
b.set_label(r'$R/R_{max}$', fontsize=24, rotation=90)

#添加图例
pos2 = ax4.get_position()
ax_bar2 = fig.add_axes([pos2.x1+0.015, pos2.y0 , 0.01, pos2.height ])
b=plt.colorbar(pcm4,shrink=0.93,orientation='vertical',extend='max',
               pad=0.035,aspect=30,cax = ax_bar2)
# 设置刻度线朝内
ticks = np.arange(0, 8.1, 2)  # 生成刻度
b.set_ticks(ticks)  # 设置刻度位置
b.set_ticklabels([f'{t:.1f}' for t in ticks], fontsize=18)  # 设置刻度标签
b.ax.tick_params(direction='in', size=3.5, width=1.5)  # size=刻度线长度, width=刻度线宽度
minor_ticks = np.arange(0, 8.1, 1)  # 包括间隔 50 的刻度
b.ax.tick_params(which='minor', direction='in', size=3, width=0.5)  # 调整次刻度线样式
b.outline.set_edgecolor('black')  # 设置边框颜色
b.outline.set_linewidth(1)  # 设置边框线宽
b.set_label(r'$RE$', fontsize=24, rotation=90)

#==========================添加图例 for union
pos3 = ax6.get_position()
ax_bar3 = fig.add_axes([pos3.x1+0.015, pos3.y0, 0.01, pos3.height ])
b=plt.colorbar(pcm6,shrink=0.93,orientation='vertical',extend='max',
               pad=0.035,aspect=30,cax = ax_bar3)
# 设置刻度线朝内
ticks = np.arange(0, 0.51, 0.1) # 生成刻度
b.set_ticks(ticks)  # 设置刻度位置
b.set_ticklabels([f'{t:.1f}' for t in ticks], fontsize=18)  # 设置刻度标签
b.ax.tick_params(direction='in', size=3.5, width=1.5)  # size=刻度线长度, width=刻度线宽度
minor_ticks = np.arange(0, 0.51, 0.05) # 包括间隔 50 的刻度
b.ax.tick_params(which='minor', direction='in', size=3, width=0.5)  # 调整次刻度线样式
b.outline.set_edgecolor('black')  # 设置边框颜色
b.outline.set_linewidth(1)  # 设置边框线宽
b.set_label(r'$DSI$', fontsize=24, rotation=90)

left = 0.04
top = 1.11
ax1.text(left, top, 'a. Day',
        horizontalalignment='center',
        verticalalignment='center',
        rotation=0,
        size=24,
        weight="bold", 
        transform=ax1.transAxes,clip_on = False) 

ax2.text(left, top, 'b. Night',
        horizontalalignment='center',
        verticalalignment='center',
        rotation=0,
        size=24,
        weight="bold", 
        transform=ax2.transAxes,clip_on = False) 
ax3.text(left, top, 'c. Day',
        horizontalalignment='center',
        verticalalignment='center',
        rotation=0,
        size=24,
        weight="bold", 
        transform=ax3.transAxes,clip_on = False) 
ax4.text(left, top, 'd. Night',
        horizontalalignment='center',
        verticalalignment='center',
        rotation=0,
        size=24,
        weight="bold", 
        transform=ax4.transAxes,clip_on = False) 
ax5.text(left, top, 'e. Day',
        horizontalalignment='center',
        verticalalignment='center',
        rotation=0,
        size=24,
        weight="bold", 
        transform=ax5.transAxes,clip_on = False) 
ax6.text(left, top, 'f. Night',
        horizontalalignment='center',
        verticalalignment='center',
        rotation=0,
        size=24,
        weight="bold", 
        transform=ax6.transAxes,clip_on = False) 
#添加经纬度标签
ax1.set_xticks([-120,0,120], crs = proj)
ax1.set_yticks(np.arange(region[-2], region[-1] + 1, 30), crs = proj)
ax1.yaxis.set_major_formatter(LatitudeFormatter())
ax1.tick_params(axis='y', labelsize=20)  # 设置字体大小
ax1.set_xlabel(""); ax1.set_ylabel("",fontsize = 20)
ax1.set_xticklabels([]) 

ax2.set_xticks([-120,0,120], crs = proj)
ax2.set_yticks(np.arange(region[-2], region[-1] + 1, 30), crs = proj)
ax2.xaxis.set_major_formatter(LongitudeFormatter())
ax2.set_xlabel(""); ax2.set_ylabel("")
ax2.set_yticklabels([]);ax2.set_xticklabels([]) 

ax3.set_xticks([-120,0,120], crs = proj)
ax3.set_yticks(np.arange(region[-2], region[-1] + 1, 30), crs = proj)
ax3.yaxis.set_major_formatter(LatitudeFormatter())
ax3.xaxis.set_major_formatter(LongitudeFormatter())
ax3.tick_params(axis='y', labelsize=20)  # 设置字体大小
ax3.tick_params(axis='x', labelsize=20)  # 设置字体大小
ax3.set_xlabel(""); ax3.set_ylabel("")
ax3.set_xticklabels([]) 

ax4.set_xticks([-120,0,120], crs = proj)
ax4.set_yticks(np.arange(region[-2], region[-1] + 1, 30), crs = proj)
ax4.xaxis.set_major_formatter(LongitudeFormatter())
ax4.set_xlabel(""); ax4.set_ylabel("")
ax4.set_yticklabels([]);ax4.set_xticklabels([]) 

ax5.set_xticks([-120,0,120], crs = proj)
ax5.set_yticks(np.arange(region[-2], region[-1] + 1, 30), crs = proj)
ax5.yaxis.set_major_formatter(LatitudeFormatter())
ax5.xaxis.set_major_formatter(LongitudeFormatter())
ax5.tick_params(axis='y', labelsize=20)  # 设置字体大小
ax5.tick_params(axis='x', labelsize=20)  # 设置字体大小
ax5.set_xlabel("",fontsize = 20); ax5.set_ylabel("",fontsize = 20)

ax6.set_xticks([-120,0,120], crs = proj)
ax6.set_yticks(np.arange(region[-2], region[-1] + 1, 30), crs = proj)
ax6.xaxis.set_major_formatter(LongitudeFormatter())
ax6.set_xlabel(""); ax6.set_ylabel("")
ax6.set_yticklabels([]) 
plt.savefig('./spatial_pattern_fig1/dsi_re_daynight.png', format='png',dpi=600,bbox_inches='tight')
# %%
