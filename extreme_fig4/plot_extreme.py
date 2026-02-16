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

region_in = nc.Dataset("./data/fig3/region.nc")
region = region_in.variables["region2.tif"][::-1,:]
region_lat = region_in.variables["lat"][:]
region_lon = region_in.variables["lon"][:]
region_nan = np.where(region < 0, np.nan, region)
aa=region_nan + 0 


with nc.Dataset("./data/fig1/years_01_22.nc", 'r') as ds:
    # 获取白天和夜间降水数据
    dayprepyearly = ds.variables["dayprec"][:]
    nightprepyearly = ds.variables["nightprec"][:]

with nc.Dataset("./data/landmask_0.1deg.nc", 'r') as ds:
    # 获取白天和夜间降水数据
    mask = ds.variables["mask"][:]


folder_path = './data/fig4/d_day/'  # 传入你想读取的文件夹路径
file_prefix = 'concatenated_daily_precipitation_'  # 文件名前缀
light_var = 'D_daily'  # 白天降水的变量名
dark_var = 'D_daily_extreme'  # 夜间降水的变量名
daytime_re_daily_yearly, day_re_extreme_yearly = calculate_annual_precipitation_yearly(folder_path, file_prefix, light_var, dark_var)
daytime_re_daily_mean, day_re_extreme_mean = calculate_annual_precipitation_mean(folder_path, file_prefix, light_var, dark_var)

folder_path = './data/fig4/d_night/'  # 传入你想读取的文件夹路径
file_prefix = 'concatenated_daily_precipitation_'  # 文件名前缀
light_var = 'D_daily'  # 白天降水的变量名
dark_var = 'D_daily_extreme'  # 夜间降水的变量名
nighttime_re_daily_yearly, night_re_extreme_yearly = calculate_annual_precipitation_yearly(folder_path, file_prefix, light_var, dark_var)
nighttime_re_daily_mean, night_re_extreme_mean = calculate_annual_precipitation_mean(folder_path, file_prefix, light_var, dark_var)

# day_re_ratio_mean = (day_re_extreme_mean / daytime_re_daily_mean) *100
# night_re_ratio_mean = (night_re_extreme_mean / nighttime_re_daily_mean) *100
# day_re_ratio_mean = np.ma.where(np.ma.getmaskarray(mask), np.ma.masked, day_re_ratio_mean)
# night_re_ratio_mean = np.ma.where(np.ma.getmaskarray(mask), np.ma.masked, night_re_ratio_mean)

day_re_ratio_yearly = (day_re_extreme_yearly / daytime_re_daily_yearly) *100
night_re_ratio_yearly = (night_re_extreme_yearly / nighttime_re_daily_yearly) *100
day_re_ratio_yearly = np.ma.where(np.ma.getmaskarray(mask), np.ma.masked, day_re_ratio_yearly)
night_re_ratio_yearly = np.ma.where(np.ma.getmaskarray(mask), np.ma.masked, night_re_ratio_yearly)

day_re_ratio_mean = np.nanmean(day_re_ratio_yearly,axis=0)
night_re_ratio_mean = np.nanmean(night_re_ratio_yearly,axis=0)


#%% 制作趋势线
day_means = np.nanmean(day_re_ratio_yearly,axis=(1,2))
night_means = np.nanmean(night_re_ratio_yearly,axis=(1,2))
years = np.arange(2001, 2023)  # 假设22年对应年份1到22
df_trend = pd.DataFrame({
    'Year': np.concatenate([years, years]),  # 重复年份列
    'Value': np.concatenate([day_means, night_means]),  # 合并数值
    'Type': ['Day'] * len(years) + ['Night'] * len(years)  # 添加类别标签
})

#%%
import math

df_prd11=pd.DataFrame({'region':aa.flatten(),'re':day_re_ratio_mean.flatten()})
df_prd11=df_prd11.dropna()
df_prd12=df_prd11[df_prd11['re'] != -math.inf]
df_prd12=df_prd12.dropna()
df_prd12.insert(df_prd12.shape[1],'time',"day")

df_prd21=pd.DataFrame({'region':aa.flatten(),'re':night_re_ratio_mean.flatten()})
df_prd21=df_prd21.dropna()
df_prd22=df_prd21[df_prd21['re']!=-math.inf]
df_prd22=df_prd22.dropna()
df_prd22.insert(df_prd22.shape[1],'time',"night")

df = pd.concat([df_prd12,df_prd22],axis=0) 
replace_dict = {
    1: 'ALA',
    2: 'AMZ',
    3: 'CAM',
    4: 'CAS',
    5: 'CEU',
    6: 'CGI',
    7: 'CNA',
    8: 'EAF',
    9: 'EAS',
    10: 'ENA',
    11: 'MED',
    12: 'NAS',
    13: 'NAU',
    14: 'NEB',
    15: 'NEU',
    16: 'SAF',
    17: 'SAH',
    18: 'SAS',
    19: 'SAU',
    20: 'SEA',
    21: 'SSA',
    22: 'TIB',
    23: 'WAF',
    24: 'WAS',
    25: 'WNA',
    26: 'WSA'
}

# 使用 replace() 函数进行替换
df['region'] = df['region'].replace(replace_dict)

region_sum_re = (
    df.groupby(['region', 'time'])['re'].mean()  # 分组计算均值
    .unstack('time')  # 将time列拆分为day/night两列[5](@ref)
    .sum(axis=1)  # 计算每行的day+night均值总和
    .sort_values(ascending=False)  # 按总和降序排序[4](@ref)
)

region_order_re = region_sum_re.index.tolist()  # 生成排序后的分区顺序




#%%
#prec14_ratio=np.log10(prec14_ratio.data)
size1 = 18
fontdict = {'weight': 'bold','size':size1,'family':'SimHei'}
mpl.rcParams.update(
    {
        'text.usetex': False,                  # 不使用 LaTeX 渲染
        #'font.family': 'sans-serif',           # 设置字体为 sans-serif
        'font.sans-serif': ['Arial'],          # 指定 sans-serif 字体（如 Arial）
        'mathtext.fontset': 'stix',            # 数学字体设置为 stix
        'font.size': 18                    # 设置全局字体大小
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

boundaries = np.arange(0, 61, 5)  # 适用于后 2 个子图
norm = BoundaryNorm(boundaries, cmap.N, extend='max')

boundaries = np.arange(-30, 31, 5)  # 适用于后 2 个子图
norm2 = BoundaryNorm(boundaries, cmap2.N, extend='max')

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
fig, ((ax1, ax2)) = plt.subplots(2, 1, figsize=(16, 10), subplot_kw={"projection": ccrs.PlateCarree()})
region = [-180, 180, -60, 60]
plt.subplots_adjust(wspace=0.1)
for ax in [ax1, ax2]:
    ax.set_extent([-180, 180, -60, 60], crs=ccrs.PlateCarree())
    ax.coastlines(linewidth=0.5)

pos2 = ax2.get_position()
ax_line = fig.add_axes([pos2.x0, pos2.y0-0.42 , pos2.width, pos2.height ])

pos = ax_line.get_position()
ax1_bar = fig.add_axes([pos.x1+0.12, pos.y0, pos.height*0.5, pos.height*3.40 ])

sns.lineplot(
    data=df_trend,
    x='Year',
    y='Value',
    hue='Type',
    palette= ["#de9e83","#142f83"],
    marker='o',           # 添加数据点标记
    markersize=8,
    linewidth=2.5,
    legend=False,
    linestyle='--',
    ax = ax_line
)
ax_line.set_xlabel('Year', fontsize=18)
ax_line.set_ylabel('EP (%)', fontsize=18)
ax_line.tick_params(axis='x', labelsize=16)  # 设置字体大小
# 分别为白天和黑夜数据添加统计信息
day_data = df_trend[df_trend['Type'] == 'Day']
night_data = df_trend[df_trend['Type'] == 'Night']


res_day = theilslopes(day_data['Value'], day_data['Year'],  alpha=0.95)
res_night = theilslopes(night_data['Value'], night_data['Year'], alpha=0.95)

# 提取结果组件（修正）
slope_day, intercept_day, slope_low_day, slope_high_day = res_day[0], res_day[1], res_day[2], res_day[3]
slope_night, intercept_night, slope_low_night, slope_high_night = res_night[0], res_night[1], res_night[2], res_night[3]

# 生成趋势线和置信区间（修正）
trend_line_day = intercept_day + slope_day * day_data['Year']
trend_line_night = intercept_night + slope_night * night_data['Year']

# 绘制Sen's趋势线（改为实线更醒目）
ax_line.plot(day_data['Year'], trend_line_day, color='#de9e83', linewidth=2, alpha=0.9, linestyle='-')
ax_line.plot(night_data['Year'], trend_line_night, color='#142f83', linewidth=2, alpha=0.9, linestyle='-')

text_day = f"Day slope: {slope_day:.2f}* (%/Year)"
text_night = f"Night slope: {slope_night:.2f}* (%/Year)"

# 添加文本框
ax_line.text(0.03, 0.95, text_day, transform=ax_line.transAxes, 
             ha='left', va='top', fontsize=16, color='#de9e83',
             bbox=None)
ax_line.text(0.03, 0.82, text_night, transform=ax_line.transAxes, 
             ha='left', va='top', fontsize=16, color='#142f83',
             bbox=None)
ax_line.tick_params(axis='x', labelsize=16)  # Adjust x-axis tick label size
ax_line.tick_params(axis='y', labelsize=16) 

pcm1 = plot_geospatial_data(ax1, lon, lat, day_re_ratio_mean[:,:], 
                          cmap=cmap, norm=norm,
                          land_color='lightgray',
                          land_alpha=0.6)
pcm2 = plot_geospatial_data(ax2, lon, lat, night_re_ratio_mean[:,:], 
                          cmap=cmap, norm=norm,
                          land_color='lightgray',
                          land_alpha=0.6)
pos4 = ax2.get_position()
ax_bar = fig.add_axes([pos4.x1+0.02, pos4.y0+0.04, 0.012,pos4.height*2 ])
b=plt.colorbar(pcm1,shrink=0.93,orientation='vertical',extend='max',
               pad=0.035,aspect=30,cax = ax_bar)
# 设置刻度线朝内
ticks = np.arange(0, 61, 20) # 生成刻度
b.set_ticks(ticks)  # 设置刻度位置
b.set_ticklabels([f'{t:.0f}' for t in ticks], fontsize=16)  # 设置刻度标签
b.ax.tick_params(direction='in', size=3.5, width=1.5)  # size=刻度线长度, width=刻度线宽度
minor_ticks = np.arange(0, 61, 10) # 包括间隔 50 的刻度
b.ax.tick_params(which='minor', direction='in', size=3, width=0.5)  # 调整次刻度线样式
b.outline.set_edgecolor('black')  # 设置边框颜色
b.outline.set_linewidth(1)  # 设置边框线宽
b.set_label('EP (%)', fontsize=16, rotation=90)

ax1.set_xticks([-120,0,120], crs = proj)
ax1.set_yticks(np.arange(region[-2], region[-1] + 1, 30), crs = proj)
ax1.yaxis.set_major_formatter(LatitudeFormatter())
ax1.xaxis.set_major_formatter(LongitudeFormatter())
ax1.tick_params(axis='y', labelsize=16)  # 设置字体大小
ax1.set_xlabel(""); ax1.set_ylabel("")
ax1.set_xticklabels([]) 

ax2.set_xticks([-120,0,120], crs = proj)
ax2.set_yticks(np.arange(region[-2], region[-1] + 1, 30), crs = proj)
ax2.yaxis.set_major_formatter(LatitudeFormatter())
ax2.xaxis.set_major_formatter(LongitudeFormatter())
ax2.set_xlabel(""); ax2.set_ylabel("")
ax1.tick_params(axis='x', labelsize=16)  # 设置字体大小
ax1.tick_params(axis='y', labelsize=16)  # 设置字体大小

sns.barplot(data=df, x="re", y="region", hue="time", palette= ["#de9e83","#293F81"],
            errorbar=('sd'),capsize=0.08,errcolor="gray",
            order=region_order_re,ax=ax1_bar,edgecolor="black")
ax1_bar.legend(title = None, ncol=2,loc="best", 
               bbox_to_anchor=(0.18, 1.04),
               frameon=False,handletextpad=0.2,prop={'size': 15})
ax1_bar.set_xlabel('EP (%)',fontsize = 18)
ax1_bar.set_ylabel('',fontsize = 14)
ax1_bar.tick_params(axis='x', labelsize=16)  # Adjust x-axis tick label size
ax1_bar.tick_params(axis='y', labelsize=16) 


left = 0.02
top = 1.06
ax1.text(left, top, 'a',
        horizontalalignment='center',
        verticalalignment='center',
        rotation=0,
        size=20,
        weight="bold", 
        transform=ax1.transAxes,clip_on = False) 

ax2.text(left, top, 'b',
        horizontalalignment='center',
        verticalalignment='center',
        rotation=0,
        size=20,
        weight="bold", 
        transform=ax2.transAxes,clip_on = False) 
ax_line.text(left, top, 'c',
        horizontalalignment='center',
        verticalalignment='center',
        rotation=0,
        size=20,
        weight="bold", 
        transform=ax_line.transAxes,clip_on = False) 
ax1_bar.text(left, 1.02, 'd',
        horizontalalignment='center',
        verticalalignment='center',
        rotation=0,
        size=20,
        weight="bold", 
        transform=ax1_bar.transAxes,clip_on = False) 
plt.savefig('./extreme_fig4/extreme_contributor.png', format='png',dpi=600,bbox_inches='tight')

