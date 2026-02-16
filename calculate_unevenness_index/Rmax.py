# -*- coding: utf-8 -*-
import os
from netCDF4 import Dataset, date2num
import numpy as np

def calculate_annual_precipitation(input_file, output_file):
    with Dataset(input_file, 'r') as ds:
        latitudes = ds.variables['latitude'][:]
        longitudes = ds.variables['longitude'][:]
        
        dark_rate = ds.variables['darkDailyPrecipRate'][:]  # nighttime precipitation
        light_rate = ds.variables['lightDailyPrecipRate'][:]  # daytime precipitation
        
        annual_dark_precip = np.sum(dark_rate, axis=0)
        annual_light_precip = np.sum(light_rate, axis=0)
    
    with Dataset(output_file, 'w', format='NETCDF4') as ds_out:

        lat_dim = ds_out.createDimension('latitude', len(latitudes))
        lon_dim = ds_out.createDimension('longitude', len(longitudes))
        
        lats = ds_out.createVariable('latitude', 'f4', ('latitude',))
        lons = ds_out.createVariable('longitude', 'f4', ('longitude',))
        
        lats.units = 'degrees_north'
        lats.long_name = 'latitude'
        lons.units = 'degrees_east'
        lons.long_name = 'longitude'
        
        lats[:] = latitudes
        lons[:] = longitudes
        
        dark_precip_var = ds_out.createVariable('annualDarkPrecipitation', 'f4', ('latitude', 'longitude'), zlib=True, complevel=9)
        light_precip_var = ds_out.createVariable('annualLightPrecipitation', 'f4', ('latitude', 'longitude'), zlib=True, complevel=9)
        
        dark_precip_var.units = "mm"
        dark_precip_var.long_name = "annual Dark Precipitation Total"
        light_precip_var.units = "mm"
        light_precip_var.long_name = "annual Light Precipitation Total"
        
        dark_precip_var[:, :] = annual_dark_precip
        light_precip_var[:, :] = annual_light_precip

    print(f"Annual precipitation data saved to {output_file}")

def find_max_precipitation(base_dir, years):
    max_dark_precip = -np.inf
    max_light_precip = -np.inf
    max_dark_year = None
    max_light_year = None
    max_dark_lat = None
    max_dark_lon = None
    max_light_lat = None
    max_light_lon = None
    
    for year in years:
        input_file = os.path.join(base_dir, f'concatenated_daily_precipitation_{year}.nc')
        output_file = os.path.join(base_dir, f'annual_precipitation_{year}.nc')
        
        calculate_annual_precipitation(input_file, output_file)
        
        with Dataset(output_file, 'r') as ds:
            annual_dark_precip = ds.variables['annualDarkPrecipitation'][:]
            annual_light_precip = ds.variables['annualLightPrecipitation'][:]
            latitudes = ds.variables['latitude'][:]
            longitudes = ds.variables['longitude'][:]
            
            # find max precipitation at daytime 
            max_light_value = np.max(annual_light_precip)
            if max_light_value > max_light_precip:
                max_light_precip = max_light_value
                max_light_year = year
                index_light = np.unravel_index(np.argmax(annual_light_precip), annual_light_precip.shape)
                max_light_lat = latitudes[index_light[0]]
                max_light_lon = longitudes[index_light[1]]
            
            # find max precipitation at nighttime
            max_dark_value = np.max(annual_dark_precip)
            if max_dark_value > max_dark_precip:
                max_dark_precip = max_dark_value
                max_dark_year = year
                index_dark = np.unravel_index(np.argmax(annual_dark_precip), annual_dark_precip.shape)
                max_dark_lat = latitudes[index_dark[0]]
                max_dark_lon = longitudes[index_dark[1]]

    print(f"The maximum annual dark precipitation is {max_dark_precip} mm in the year {max_dark_year}, at latitude {max_dark_lat} and longitude {max_dark_lon}.")
    print(f"The maximum annual light precipitation is {max_light_precip} mm in the year {max_light_year}, at latitude {max_light_lat} and longitude {max_light_lon}.")


base_dir = ''  # data path
years = [str(year) for year in range(2001, 2023)]  

# find_max_precipitation
find_max_precipitation(base_dir, years)