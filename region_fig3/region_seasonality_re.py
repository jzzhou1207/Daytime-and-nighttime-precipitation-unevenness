#%% 导入library
import netCDF4 as nc
from netCDF4 import Dataset
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
import math
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
import pandas as pd
from cartopy.mpl.ticker import LatitudeFormatter, LongitudeFormatter
import seaborn as sns
import scipy.stats as stats
import matplotlib.gridspec as gridspec

#%% 读取不同地理分区的平均S值

def calculate_annual_precipitation_mean(folder_path,file_prefix,light_var, dark_var):
    # 查找文件夹中的.nc文件
    file_pattern = os.path.join(folder_path, f'{file_prefix}*.nc')
    nc_files = sorted(glob.glob(file_pattern))[:]  # 读取所有年份
    
    # 初始化空列表，用于存储白天和夜间降水数据
    all_day_data = []
    all_night_data = []
    
    # 循环读取所有文件
    for nc_file in nc_files:
        # 打开.nc文件
        with Dataset(nc_file, 'r') as ds:
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
def calculate_annual_precipitation_mean2(folder_path,file_prefix,daily_var,light_var, dark_var):
    # 查找文件夹中的.nc文件
    file_pattern = os.path.join(folder_path, f'{file_prefix}*.nc')
    nc_files = sorted(glob.glob(file_pattern))[:]  # 读取所有年份
    
    # 初始化空列表，用于存储白天和夜间降水数据
    all_daily_data = []
    all_day_data = []
    all_night_data = []
    
    # 循环读取所有文件
    for nc_file in nc_files:
        # 打开.nc文件
        with Dataset(nc_file, 'r') as ds:
            # 获取白天和夜间降水数据
            daily_data = ds.variables[daily_var][:]
            daily_data = np.squeeze(daily_data)
            day_data = ds.variables[light_var][:]
            day_data = np.squeeze(day_data)
            night_data = ds.variables[dark_var][:]
            night_data = np.squeeze(night_data)
            
            # 将数据添加到列表中
            all_daily_data.append(daily_data)
            all_day_data.append(day_data)
            all_night_data.append(night_data)
    
    # 将所有数据合并为一个大的数组
    all_daily_data2 = np.stack(all_daily_data, axis=0)
    all_day_data2 = np.stack(all_day_data, axis=0)
    all_night_data2 = np.stack(all_night_data, axis=0)
    
    # 计算白天和夜间降水的平均值
    dailymean = np.nanmean(all_daily_data2, axis=0)
    daymean = np.nanmean(all_day_data2, axis=0)
    nightmean = np.nanmean(all_night_data2, axis=0)
    
    return dailymean,daymean, nightmean
#%%
region_in = nc.Dataset("/data1/ZhouJZ/precipitation/season/region.nc")
region = region_in.variables["region2.tif"][::-1,:]
region_lat = region_in.variables["lat"][:]
region_lon = region_in.variables["lon"][:]

folder_path = '/data1/zlzhang/dark_light_pre/D_index_light/'  # 传入你想读取的文件夹路径
file_prefix = 'concatenated_daily_precipitation_'  # 文件名前缀
light_var = 'D_daily'  # 白天降水的变量名
dark_var = 'D_monthly'  # 夜间降水的变量名
day_s_daily_mean2, day_s_monthly_mean2 = calculate_annual_precipitation_mean(folder_path, file_prefix, light_var, dark_var)

folder_path = '/data1/zlzhang/dark_light_pre/D_index_night/'  # 传入你想读取的文件夹路径
file_prefix = 'concatenated_daily_precipitation_'  # 文件名前缀
light_var = 'D_daily'  # 白天降水的变量名
dark_var = 'D_monthly'  # 夜间降水的变量名
night_s_daily_mean2, night_s_monthly_mean2 = calculate_annual_precipitation_mean(folder_path, file_prefix, light_var, dark_var)

folder_path = '/data1/ZhouJZ/precipitation/season/gpm/dsi_nightmax/'  # 传入你想读取的文件夹路径
file_prefix = 'concatenated_daily_precipitation_'  # 文件名前缀
light_var = 'S_daily'  # 白天降水的变量名
dark_var = 'S_monthly'  # 夜间降水的变量名
day_dsi_daily_mean2, day_dsi_monthly_mean2 = calculate_annual_precipitation_mean(folder_path, file_prefix, light_var, dark_var)

folder_path = '/data1/zlzhang/dark_light_pre/S_night_index/'  # 传入你想读取的文件夹路径
file_prefix = 'concatenated_daily_precipitation_'  # 文件名前缀
light_var = 'S_daily'  # 白天降水的变量名
dark_var = 'S_monthly'  # 夜间降水的变量名
night_dsi_daily_mean2, night_dsi_monthly_mean2 = calculate_annual_precipitation_mean(folder_path, file_prefix, light_var, dark_var)



nc_precmean = nc.Dataset("/data1/jzhang/datasets/gpm_3imerghh/0.5hour_direct/modify_index/prec_summary_index_2001_2022_0.1deg_modify.nc")
lon=nc_precmean.variables['longitude'][:]
lat=nc_precmean.variables['latitude'][:]
nc_precmean.close()


#白天的S和夜间的S不进行归一化，读取contribution
region_nan = np.where(region < 0, np.nan, region)
aa=region_nan + 0 
df_prd11=pd.DataFrame({'region':aa.flatten(),'value':day_s_daily_mean2.flatten(),
                       'value_contribution':day_dsi_daily_mean2.flatten()})
df_prd11=df_prd11.dropna()
df_prd12=df_prd11[df_prd11['value'] != -math.inf]
df_prd12=df_prd12.dropna()
df_prd12.insert(df_prd12.shape[1],'time',"day")

df_prd21=pd.DataFrame({'region':aa.flatten(),'value':night_s_daily_mean2.flatten(),
                       'value_contribution':night_dsi_daily_mean2.flatten()})
df_prd21=df_prd21.dropna()
df_prd22=df_prd21[df_prd21['value']!=-math.inf]
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

region_sum = (
    df.groupby(['region', 'time'])['value'].mean()  # 分组计算均值
    .unstack('time')  # 将time列拆分为day/night两列[5](@ref)
    .sum(axis=1)  # 计算每行的day+night均值总和
    .sort_values(ascending=False)  # 按总和降序排序[4](@ref)
)
region_sum_dsi = (
    df.groupby(['region', 'time'])['value_contribution'].mean()  # 分组计算均值
    .unstack('time')  # 将time列拆分为day/night两列[5](@ref)
    .sum(axis=1)  # 计算每行的day+night均值总和
    .sort_values(ascending=False)  # 按总和降序排序[4](@ref)
)
region_order = region_sum.index.tolist()  # 生成排序后的分区顺序
region_order_dsi = region_sum_dsi.index.tolist()

#%% 读取不同地区每日降水分布，
def calculate_annual_precipitation_mean(folder_path,file_prefix,light_var, dark_var,lon,lat,output_file):
    # 查找文件夹中的.nc文件
    file_pattern = os.path.join(folder_path, f'{file_prefix}*.nc')
    nc_files = glob.glob(file_pattern)[0:11]

    all_day_data = []
    all_night_data = []
    
    # 循环读取所有文件
    for nc_file in nc_files:
        # 打开.nc文件
        with Dataset(nc_file, 'r') as ds:
            # 获取白天和夜间降水数据
            day_data = ds.variables[light_var][0:365,:,:] #只选择前365天
            day_data = np.squeeze(day_data)
            night_data = ds.variables[dark_var][0:365,:,:]#只选择前365天
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

    # 保存 daymean 和 nightmean 到一个新的 .nc 文件
    with Dataset(output_file, 'w', format='NETCDF4') as ds_out:
        # 获取数据的维度
        lat_dim = 1800;lon_dim = 3600;time_dim = 365
        ti = np.arange(1,366)
        # 创建维度
        ds_out.createDimension('time', time_dim)
        ds_out.createDimension('lat', lat_dim)
        ds_out.createDimension('lon', lon_dim)

        longitude = ds_out.createVariable('Longitude','f4','lon')
        latitude  = ds_out.createVariable('Latitude','f4','lat')
        time = ds_out.createVariable('Time','i4','tim')
        # 创建变量
        daymean_var = ds_out.createVariable('daymean', np.float32, ('time', 'lat', 'lon'))
        nightmean_var = ds_out.createVariable('nightmean', np.float32, ('time', 'lat', 'lon'))
        # 将数据写入变量

        longitude[:] = lon
        latitude[:] = lat
        time[:] = ti
        daymean_var[:] = daymean
        nightmean_var[:] = nightmean
        
        # 添加单位或其他属性（根据需要）
        daymean_var.units = 'mm/day'  # 示例单位
        nightmean_var.units = 'mm/day'  # 示例单位

    print(f"文件已保存: {output_file}")
nc_in = nc.Dataset("/data1/ZhouJZ/precipitation/season/gpm/daily_prec/daily_average.nc")
d_daily = nc_in.variables["lightDailyPrecipRate"][:]
n_daily = nc_in.variables["darkDailyPrecipRate"][:]
nc_in.close()

region_in = nc.Dataset("/data1/ZhouJZ/precipitation/season/region.nc")
region = region_in.variables["region2.tif"][::-1,:]
region_lat = region_in.variables["lat"][:]
region_lon = region_in.variables["lon"][:]

reshaped_d_daily = d_daily.reshape(365, -1)
reshaped_n_daily = n_daily.reshape(365, -1)
df_d = pd.DataFrame(reshaped_d_daily).T
region_nan = np.where(region < 0, np.nan, region)
aa=region_nan + 0 
df_aa=pd.DataFrame({'region':aa.flatten()})
df_prd11 = pd.concat([df_aa, df_d], axis=1)
df_prd11=df_prd11.dropna()
df_prd11.insert(df_prd11.shape[1],'time',"day")

df_n = pd.DataFrame(reshaped_n_daily).T
df_prd21 = pd.concat([df_aa, df_n], axis=1)
df_prd21=df_prd21.dropna() 
df_prd21.insert(df_prd21.shape[1],'time',"night")
df_daily = pd.concat([df_prd11,df_prd21],axis=0) 
df_daily['region'] = df_daily['region'].replace(replace_dict)
df_avg = df_daily.groupby(['region', 'time']).mean().reset_index()


# %% 绘图
regions = region_order[:10]
colors = plt.cm.tab10.colors[:10]
fig = plt.figure(figsize=(16, 12))
# 使用一个 GridSpec 定义整体布局：上方是2行5列的小图（占页面的大部分），下方是条形图（只有一小部分）
gs = gridspec.GridSpec(4, 5, figure=fig, height_ratios=[1, 1, 0.5,0.5], hspace=0.3, wspace=0.3)
# 创建顶部的10个子图（2行5列）
axs_top = [fig.add_subplot(gs[i, j]) for i in range(2) for j in range(5)]
# 创建底部的条形图（在第三行，独占一行，宽度跨越全部5列）
ax2 = fig.add_subplot(gs[2, :])
ax3 = fig.add_subplot(gs[3, :])


# 遍历每个地区和对应的子图
for idx, (ax, region) in enumerate(zip(axs_top, regions)):
    # 提取该地区的白天和夜晚数据
    day_data = df_avg[(df_avg['region'] == region) & (df_avg['time'] == 'day')].iloc[:, 2:].values.flatten()
    night_data = df_avg[(df_avg['region'] == region) & (df_avg['time'] == 'night')].iloc[:, 2:].values.flatten()
    day_data_series = pd.Series(day_data/np.sum(day_data)*100)
    night_data_series = pd.Series(night_data/np.sum(night_data)*100)
    # 绘制折线（白天用实线，夜晚用虚线）
    sns.lineplot(x=range(365), y=day_data/np.sum(day_data)*100, ax=ax,color='#de9e83', linestyle='-', linewidth=0.5,alpha=0.3)
    sns.lineplot(x=range(365), y=night_data/np.sum(night_data)*100, ax=ax,color='#142f83', linestyle='-',linewidth=0.5,alpha=0.3)
    day_rolling = day_data_series.rolling(window=5).mean()
    night_rolling = night_data_series.rolling(window=5).mean()
    sns.lineplot(x=range(365), y=day_rolling, ax=ax, color="#de9e83", linestyle='-', linewidth=1)
    sns.lineplot(x=range(365), y=night_rolling, ax=ax, color="#142f83", linestyle='-', linewidth=0.8)

    # 设置子图标题和网格
    ax.set_title(region, fontsize=14)
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.tick_params(axis='y', labelsize=12) 
    # 仅在最左侧子图显示 y 轴标签
    if idx % 5 == 0:
        ax.set_ylabel('Precipitation distribution (%)', fontsize=14)
    else:
        ax.set_ylabel('')
    
    # 仅在最下方子图显示 x 轴标签
    if idx >= 5:
        ax.set_xlabel('DOY', fontsize=14)
        ax.set_xticks([1, 100, 200, 300])
        ax.tick_params(axis='x', labelsize=12) 
    else:
        ax.set_xticks([1, 100, 200, 300])
        ax.set_xticklabels([])

sns.barplot(data=df, x="region", y="value", hue="time", palette= ["#de9e83","#142f83"],
            errorbar=('sd'),capsize=0.08,errcolor="gray",
            order=region_order,ax=ax2,edgecolor="black")
ax2.legend(title = None, ncol=2,loc="upper right",frameon=False,handletextpad=0.2,prop={'size': 14})
ax2.set_ylabel('RE',fontsize = 14)
ax2.set_xlabel('',fontsize = 14)
ax2.tick_params(axis='x', labelsize=14)  # Adjust x-axis tick label size
ax2.tick_params(axis='y', labelsize=14) 

sns.barplot(data=df, x="region", y="value_contribution", hue="time", palette= ["#de9e83","#142f83"],
            errorbar=('sd'),capsize=0.08,errcolor="gray",
            order=region_order_dsi,ax=ax3,edgecolor="black")
ax3.legend(title = None, ncol=2,loc="upper right",frameon=False,handletextpad=0.2,prop={'size': 14})
ax3.set_ylabel('DSI',fontsize = 14)
ax3.set_xlabel('Region',fontsize = 14)
ax3.tick_params(axis='x', labelsize=14)  # Adjust x-axis tick label size
ax3.tick_params(axis='y', labelsize=14) 
#ax3.set_ylim(0,100)
#ax3.axhline(y=50, color='lightgray', linestyle='--', linewidth=2)

plt.savefig('./dsi_re_region_realdsi_re2.png', format='png',dpi=600,bbox_inches='tight')

# %%
