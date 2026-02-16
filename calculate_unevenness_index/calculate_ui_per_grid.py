# -*- coding: utf-8 -*-
import xarray as xr
import numpy as np
import os
from multiprocessing import Pool, cpu_count
from functools import partial
import gc
import time
import pandas as pd



# Functions to calculate seasonality indices
def calculate_seasonality_index(ds):
    """
    Calculate daily and monthly seasonality index (S) for each grid point using xarray.
    Args:
        ds (xarray.Dataset): Dataset containing precipitation data
    Returns:
        xarray.DataArray: Daily seasonality index for each grid point
    """
    if not np.issubdtype(ds['time'].dtype, np.datetime64):
        ds['time'] = pd.to_datetime(ds['time'].values)  # Convert to datetime64
        ds['time'] = xr.DataArray(ds['time'], dims='time')

    
    # max annual precipitation (mm) among all grids during 1950-2023
    Rmax = 7959.97021 # for all max precipitation is nighttime maxmium precipitation 
    precipitation = ds['lightDailyPrecipRate']  # Precipitation data (time, lat, lon)
    precipitation = precipitation.where(precipitation>=0, 0)
    R = precipitation.sum(dim='time', skipna=True)  # Total precipitation for each grid point
    
    # cal daily seasonality index
    m = precipitation.sizes['time']  # Number of time steps, 365 or 366
    q = 1 / m  # Average proportion q
    # Avoid division by zero
    valid = R > 0
    pi = xr.where(valid, precipitation / R, np.nan)  # Proportion of precipitation (pi)
    # Compute seasonality index D
    #D = xr.where(valid,(pi * np.log2(pi / q)),np.nan)
    D = xr.where(pi > 0, (pi * np.log2(pi / q)), 0)
    D = D.sum(dim='time', skipna=True)
    S_daily = D * R / Rmax # if necessary
    S_daily = S_daily.where(valid, np.nan)
    
    # cal monthly seasonality index
    monthly_precip = precipitation.resample(time='1ME').sum(dim='time', skipna=True)  # Monthly total precipitation
    q = 1 / 12  # Average proportion q
    # Avoid division by zero
    valid = R > 0
    pi = xr.where(valid, monthly_precip / R, np.nan)  # Proportion of precipitation (pi)
    # Compute seasonality index D
    #D = xr.where(valid,(pi * np.log2(pi / q)),np.nan)
    D = xr.where(pi > 0, (pi * np.log2(pi / q)), np.nan)
    D = D.sum(dim='time', skipna=True)
    S_monthly = D * R / Rmax
    S_monthly = S_monthly.where(valid, np.nan)
    del precipitation, monthly_precip, R, valid, pi, D
    gc.collect()
    
    return S_daily, S_monthly



# Function to process a single NetCDF file and save results
def process_and_save(file_path, output_dir):
    """
    Process a single NetCDF file to compute daily and monthly seasonality indices for all grid points.
    Args:
        file_path (str): Path to the NetCDF file
    Returns:
        xarray.Dataset: Dataset containing daily and monthly seasonality indices
    """
    
    print(f"Start processing: {file_path}")
    
    t1 = time.time()
    
    # Open the NetCDF file
    ds = xr.open_dataset(file_path,decode_times=True)

    # Compute daily and monthly seasonality indices
    S_daily, S_monthly = calculate_seasonality_index(ds)

    # add time info
    #year = int(file_path[-7:-3])
    year = int(file_path.split("_")[-1].split(".")[0])

    time_info = xr.DataArray([year], dims=["time"], coords={"time": [year]}, name="time")
    S_daily = S_daily.expand_dims(dim='time').assign_coords(time=time_info)
    S_monthly = S_monthly.expand_dims(dim='time').assign_coords(time=time_info)
    
    # Combine results into a new Dataset
    result_ds = xr.Dataset({
        'S_daily': S_daily,
        'S_monthly': S_monthly
    })

    # Save the result to a NetCDF file
    filename = os.path.basename(file_path).replace('.nc', '_seasonality_indices_light.nc')
    output_path = os.path.join(output_dir, filename)
    result_ds.to_netcdf(output_path)
    
    t2 = time.time()
    running_time = t2-t1
    
    print(f"Processed and saved: {output_path}, running time = {running_time}s")
    
    ds.close()
    del ds, S_daily, S_monthly, result_ds
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
