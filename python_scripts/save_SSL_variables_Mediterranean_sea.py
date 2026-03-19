#!/usr/bin/env python
# Collect SSLs variables from only Mediterranean sea (discard Black sea data)

import os
import pandas as pd
import numpy as np

directory = os.path.dirname(os.path.abspath(__file__))

# Collect SSLs variables (from SSLs_detection.py)
df = pd.read_csv(os.path.join(directory, 'Save_variables.csv'))  

final_df_Med_sea = pd.DataFrame(columns=['WMO', 'cycle', 'Longitude','Latitude','Year', 'Month', 'Day', 'SG_min','Depth','TG','PDAG', 'Schmidt_stability'])

for i in range(len(df['WMO'])) :
    
    if df['Longitude'][i] >= 28.418 and df['Longitude'][i] <= 41.602 and df['Latitude'][i] >= 40.730 and df['Latitude'][i] <= 45.081 :
        print('Black sea data')
        
    else :
        WMO = df['WMO'].iloc[i]
        cycle = df['cycle'].iloc[i]
        longitude = df['Longitude'].iloc[i]
        latitude = df['Latitude'].iloc[i]
        year = df['Year'].iloc[i]
        month = df['Month'].iloc[i]
        day = df['Day'].iloc[i]
        SG_min = df['SG_min'].iloc[i]
        depth_SG_min = df['Depth'].iloc[i]
        TG_val = df['TG'].iloc[i]
        PDAG_val = df['PDAG'].iloc[i]
        Schmidt_stability = df['Schmidt_stability'].iloc[i] 

        df_new_row = pd.DataFrame(data=np.array([[WMO, cycle, longitude, latitude, year, month, day, SG_min, depth_SG_min, TG_val, PDAG_val, Schmidt_stability]]), columns=['WMO', 'cycle', 'Longitude','Latitude','Year', 'Month', 'Day', 'SG_min','Depth','TG','PDAG', 'Schmidt_stability'])
        df_final_Med_sea = pd.concat([final_df_Med_sea,df_new_row], ignore_index=True)


df_final_Med_sea.to_csv(os.path.join(directory, "SLLs_variables_Mediterranean_sea.csv"))
