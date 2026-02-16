# -*- coding: utf-8 -*-
import xarray as xr
import numpy as np
import os
from multiprocessing import Pool, cpu_count
from functools import partial
import gc
import time
import pandas as pd



# Functions to calculate D values only
def calculate_D_values(ds):
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

    # Rmax = 7959.97021
    precipitation = ds['darkDailyPrecipRate']
    precipitation = precipitation.where(precipitation>=0, 0)
    R = precipitation.sum(dim='time', skipna=True)

    # Calculate daily D value
    m = precipitation.sizes['time']
    q_daily = 1 / m
    valid_daily = R > 0
    pi_daily = xr.where(valid_daily, precipitation / R, np.nan)
    D_daily = xr.where(pi_daily > 0, (pi_daily * np.log2(pi_daily / q_daily)), 0)
    D_daily = D_daily.sum(dim='time', skipna=True)

    # Calculate monthly D value
    monthly_precip = precipitation.resample(time='1ME').sum(dim='time', skipna=True)
    q_monthly = 1 / 12
    valid_monthly = R > 0
    pi_monthly = xr.where(valid_monthly, monthly_precip / R, np.nan)
    D_monthly = xr.where(pi_monthly > 0, (pi_monthly * np.log2(pi_monthly / q_monthly)), np.nan)
    D_monthly = D_monthly.sum(dim='time', skipna=True)

    del precipitation, R, valid_daily, pi_daily, valid_monthly, pi_monthly
    gc.collect()
    
    return D_daily, D_monthly

# Function to process a single NetCDF file and save results with D values only
def process_and_save(file_path, output_dir):
    print(f"Start processing: {file_path}")
    t1 = time.time()

    ds = xr.open_dataset(file_path, decode_times=True)
    D_daily, D_monthly = calculate_D_values(ds)

    year = int(file_path.split("_")[-1].split(".")[0])
    time_info = xr.DataArray([year], dims=["time"], coords={"time": [year]}, name="time")
    D_daily = D_daily.expand_dims(dim='time').assign_coords(time=time_info)
    D_monthly = D_monthly.expand_dims(dim='time').assign_coords(time=time_info)

    result_ds = xr.Dataset({
        'D_daily': D_daily,
        'D_monthly': D_monthly
    })

    filename = os.path.basename(file_path).replace('.nc', '_D_values.nc')
    output_path = os.path.join(output_dir, filename)
    result_ds.to_netcdf(output_path)

    t2 = time.time()
    running_time = t2-t1
    print(f"Processed and saved: {output_path}, running time = {running_time}s")

    ds.close()
    del ds, D_daily, D_monthly, result_ds
    gc.collect()

    return
    
    
    
# Function to process files in parallel
def process_files_in_parallel(input_dir, output_dir, num_workers=None):
    """
    Process all NetCDF files in a directory in parallel to compute seasonality indices.
    Args:
        input_dir (str): Directory containing NetCDF files
        output_dir (str): Directory to save output files
        num_workers (int): Number of parallel workers (default: number of CPUs)
    """
    # Find all NetCDF files in the input directory
    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.nc')]

    if not files:
        raise FileNotFoundError(f"No NetCDF files found in {input_dir}")

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Use multiprocessing to process files in parallel
    num_workers = num_workers or cpu_count()
    print(f"Processing {len(files)} files using {num_workers} workers...")

    # Use a multiprocessing pool to process files
    process_and_save_with_fixed_output_dir = partial(process_and_save, output_dir=output_dir)
    with Pool(processes=num_workers) as pool:
        pool.map(process_and_save_with_fixed_output_dir, files)



# Main function
if __name__ == "__main__":
    # Define input and output directories
    input_dir = r"/path/"
    output_dir = r"/path/"

    # Process all files in parallel
    process_files_in_parallel(input_dir, output_dir, 5)
