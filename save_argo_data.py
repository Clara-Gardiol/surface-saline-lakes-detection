#!/usr/bin/env python
# Use argopy to download the argo float data
# Note: this script was written in 2024 and may not run with newer versions of argopy/numpy

import argopy

from argopy import DataFetcher, ArgoIndex
from argopy.plot import scatter_map, scatter_plot

import matplotlib.pyplot as plt
import os
import gsw
import xarray as xr
import cartopy
import geopandas

argopy.clear_cache()
directory = os.path.dirname(os.path.abspath(__file__))

# For the whole Mediterranean sea dataset :
box = [-5.918, 35.654, 30.015, 43.286, 0, 200, '2000-01', '2024-08'] # Mediterranean sea (with Black sea data careful !)
# TODO: exclude Black Sea data once SSL detection is complete

# Define an Argo data set
# https://argopy.readthedocs.io/en/latest/user-guide/fetching-argo-data/user_mode.html
# We use 'standard' in order to consider also floats that are still active and have data in "real time"
# Standard will include 1 - good and 2 - probably good data

ArgoSet = DataFetcher(mode='standard', ds='phy', cache=True, parallel=True, direction='ascending').region(box) 
ArgoSet.load()
ArgoSet.plot('trajectory')
plt.savefig(os.path.join(directory, 'Argo_trajectories.png'), dpi=300)
ds = ArgoSet.data


# Add TEOS-10 variables - potential density anomaly
# https://github.com/euroargodev/argopy/blob/0372f38fa8285b98dd4a7bfd908ce88d9e6fa7f4/argopy/xarray.py#L1386 

ds.argo.teos10(['SIG0']) # Add PDA variable (Potential Density Anomaly)
ds.argo.teos10(['PTEMP']) # Add PTEMP variable (Potential Temperature)

df_profile = ds.argo.point2profile()
df = ArgoSet.data.to_dataframe()

df.to_csv(os.path.join(directory, 'Argo_data.csv')) # Save Argo csv file into the directory
ArgoSet.data.to_netcdf(os.path.join(directory,'Argo_data.nc')) # Save netCDF file
