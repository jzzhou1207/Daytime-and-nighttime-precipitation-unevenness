#%%
# -*- coding: utf-8 -*-
import xarray as xr
import numpy as np
import os
from multiprocessing import Pool, cpu_count
from functools import partial
import gc
import time
import pandas as pd

def vectorized_extreme_D_change(precipitation, precipitation_extreme, R, m, time_dim='time'):
    # 基本参数
    valid_daily = R > 0       
    q_daily = 1 / m
    pi_daily = xr.where(valid_daily, precipitation / R, np.nan)
    D_daily = xr.where(pi_daily > 0, (pi_daily * np.log2(pi_daily / q_daily)), 0)
    if D_daily.dims[0] != time_dim:
        # 获取所有维度
        dims = list(D_daily.dims)
        # 移除时间维度
        dims.remove(time_dim)
        # 将时间维度放在最前面
        new_dims = [time_dim] + dims
        # 重新排列维度
        D_daily = D_daily.transpose(*new_dims)    
    # 计算累积D值
    D_cumulative = D_daily.cumsum(dim=time_dim, skipna=True)
    
    # 创建极端降水事件的掩膜
    #extreme_mask = precipitation_extreme > 0
    extreme_mask = xr.where(precipitation_extreme.isnull(), False, precipitation_extreme > 0)
    
    # 找到事件开始位置 (从非极端变为极端)
    # 使用shift来避免diff
    # 事件开始：当天是极端降水，且前一天不是（或者当天是第一天）
    shifted_mask_prev = extreme_mask.shift({time_dim: 1}, fill_value=False)
    starts = extreme_mask & ~shifted_mask_prev
    
    # 事件结束：当天是极端降水，且下一天不是（或者当天是最后一天）
    shifted_mask_next = extreme_mask.shift({time_dim: -1}, fill_value=False)
    ends = extreme_mask & ~shifted_mask_next
    
    start_values = D_cumulative.where(starts)
    end_values = D_cumulative.where(ends)
    
    # 对每个网格点，按时间顺序匹配开始和结束位置
    def calculate_change_for_point(start_vals, end_vals):
        # 获取非NaN的开始和结束位置
        start_times = np.where(~np.isnan(start_vals))[0]
        end_times = np.where(~np.isnan(end_vals))[0]
        
        # 确保开始和结束位置数量匹配
        n_events = min(len(start_times), len(end_times))
        if n_events == 0:
            return 0.0
        
        # 计算每个事件的变化量并求和
        total_change = 0.0
        for i in range(n_events):
            start_val = start_vals[start_times[i]]
            end_val = end_vals[end_times[i]]
            
            # 如果开始和结束发生在同一天
            if start_times[i] == end_times[i]:
                # 直接使用该天的D值开始值
                total_change += D_daily.isel({time_dim: start_times[i]})
            else:
                total_change += (end_val - start_val)
        
        return total_change
    
    # 应用函数到每个网格点
    total_change = xr.apply_ufunc(
        calculate_change_for_point,
        start_values,
        end_values,
        input_core_dims=[[time_dim], [time_dim]],
        output_core_dims=[[]],
        vectorize=True,
        dask='parallelized',
        output_dtypes=[float]
    )
    
    # 处理无效区域
    total_change = xr.where(R > 0, total_change.fillna(0), 0)
    
    return total_change

# Functions to calculate D values only
def calculate_D_values(ds,ds_extreme):
    """
    Calculate daily and monthly D values for each grid point using xarray.
    Args:
        ds (xarray.Dataset): Dataset containing precipitation data
    Returns:
        tuple: Daily and Monthly D values as xarray.DataArray
    """
    if not np.issubdtype(ds['time'].dtype, np.datetime64):
        ds['time'] = pd.to_datetime(ds['time'].values)  # Convert to datetime64
        ds['time'] = xr.DataArray(ds['time'], dims='time')
        
    if not np.issubdtype(ds_extreme['time'].dtype, np.datetime64):
        ds_extreme['time'] = pd.to_datetime(ds_extreme['time'].values)  # Convert to datetime64
        ds_extreme['time'] = xr.DataArray(ds_extreme['time'], dims='time')
    ds_extreme = ds_extreme.assign_coords(latitude=ds['latitude'])
    ds_extreme = ds_extreme.assign_coords(longitude=ds['longitude'])
    ds_extreme = ds_extreme.assign_coords(time=ds['time'])
    #Rmax = 7959.97021 # for night
    Rmax = 5748.13623046875 # for day
    precipitation = ds['lightDailyPrecipRate']
    precipitation = precipitation.where(precipitation>=0, 0)
    R = precipitation.sum(dim='time', skipna=True)

    precipitation_extreme = ds_extreme['lightPrecipRate975']
    precipitation_extreme = precipitation_extreme.where(precipitation_extreme>=0, 0)
    
    # Calculate daily D value
    m = precipitation.sizes['time']
    q_daily = 1 / m
    valid_daily = R > 0
    
    pi_daily = xr.where(valid_daily, precipitation / R, np.nan)
    D_daily = xr.where(pi_daily > 0, (pi_daily * np.log2(pi_daily / q_daily)), 0)
    D_daily = D_daily.sum(dim='time', skipna=True)
    
    pi_daily_extreme = xr.where(valid_daily, precipitation_extreme / R, np.nan)
    D_daily_extreme = xr.where(pi_daily_extreme > 0, (pi_daily_extreme * np.log2(pi_daily_extreme / q_daily)), 0)
    D_daily_extreme = D_daily_extreme.sum(dim='time', skipna=True)
    
#    # 计算极端降水事件期间的D值变化量
#    D_daily_extreme = vectorized_extreme_D_change(
#        precipitation, 
#        precipitation_extreme, 
#        R, 
#        m,
#        time_dim='time'
#    )
    
    del precipitation, R, valid_daily, pi_daily
    gc.collect()
    
    return D_daily, D_daily_extreme

# Function to process a single NetCDF file and save results with D values only
def process_and_save(file_path1, file_path2, output_dir):
    print(f"Start processing: {file_path1}")
    print(f"Start processing: {file_path2}")
    t1 = time.time()

    ds = xr.open_dataset(file_path1, decode_times=True)
    ds_extreme = xr.open_dataset(file_path2, decode_times=True)
    D_daily, D_daily_extreme = calculate_D_values(ds,ds_extreme)

    year = int(file_path1.split("_")[-1].split(".")[0])
    time_info = xr.DataArray([year], dims=["time"], coords={"time": [year]}, name="time")
    D_daily = D_daily.expand_dims(dim='time').assign_coords(time=time_info)
    D_daily_extreme = D_daily_extreme.expand_dims(dim='time').assign_coords(time=time_info)

    result_ds = xr.Dataset({
        'D_daily': D_daily,
        'D_daily_extreme': D_daily_extreme
    })

    filename = os.path.basename(file_path1).replace('.nc', '_D_values.nc')
    output_path = os.path.join(output_dir, filename)
    result_ds.to_netcdf(output_path)

    t2 = time.time()
    running_time = t2-t1
    print(f"Processed and saved: {output_path}, running time = {running_time}s")

    ds.close()
    del ds, D_daily, D_daily_extreme, result_ds
    gc.collect()

    return
    
    
    
# Function to process files in parallel
def process_files_in_parallel(input_dir1,input_dir2, output_dir, num_workers=None):
    """
    Process all NetCDF files in a directory in parallel to compute seasonality indices.
    Args:
        input_dir1 (str): Directory containing NetCDF files
        output_dir (str): Directory to save output files
        num_workers (int): Number of parallel workers (default: number of CPUs)
    """
    # Find all NetCDF files in the input directory
    files1 = sorted([os.path.join(input_dir1, f) for f in os.listdir(input_dir1) if f.endswith('.nc')])
    files2 = sorted([os.path.join(input_dir2, f) for f in os.listdir(input_dir2) if f.endswith('deg_95p_extre.nc')])

    if not files1:
        raise FileNotFoundError(f"No NetCDF files found in {input_dir1}")
    if not files2:
        raise FileNotFoundError(f"No NetCDF files found in {input_dir2}")

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Use multiprocessing to process files in parallel
    num_workers = num_workers or cpu_count()
    print(f"Processing {len(files1)} files using {num_workers} workers...")

    # Use a multiprocessing pool to process files
    process_and_save_with_fixed_output_dir = partial(process_and_save, output_dir=output_dir)
    with Pool(processes=num_workers) as pool:
        pool.starmap(process_and_save_with_fixed_output_dir, zip(files1, files2))



# Main function
if __name__ == "__main__":
    # Define input and output directories
    input_dir1 = r"/data1/zlzhang/dark_light_pre/daily_pre/"
    input_dir2 = r"/data1/jzhang/datasets/gpm_3imerghh/0.5hour_direct/prec95_remove0/"
    output_dir = r"/data1/ZhouJZ/precipitation/season/gpm/extreme/d_day/"

    # Process all files in parallel
    process_files_in_parallel(input_dir1, input_dir2,output_dir, 5)
