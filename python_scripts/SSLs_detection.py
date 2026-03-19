#!/usr/bin/env python
# Detect surface saline lakes by using argo data 

import os
import pandas as pd
import numpy as np
import gsw
import matplotlib.pyplot as plt

# Create an empty DataFrame to check Schmidt stability calculation :
df_check_SSI = pd.DataFrame(columns=['WMO', 'cycle', 'z0', 'zd', 'zg', 'z', 'density_g', 'density_z','dz', 'SSI'])

# Collect argo data (from save_argo_data.py)
directory = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(directory, 'Argo_data.csv'), parse_dates=['TIME'])   

# Add an in-situ density column through the TEOS-10 library :
df['SA']   =  gsw.SA_from_SP(df['PSAL'], df['PRES'], df['LONGITUDE'], df['LATITUDE']) # Absolute salinity (g/kg)
df['rho']   = gsw.density.rho_t_exact(df['SA'], df['TEMP'], df['PRES']) # In-situ density

print(df.PLATFORM_NUMBER.unique()) 
unique_WMO = df.PLATFORM_NUMBER.unique()

## Create an empty DataFrame and store surface saline lakes variables inside
final_df = pd.DataFrame(columns=['WMO', 'cycle', 'Longitude','Latitude','Year', 'Month', 'Day', 'SG_min','Depth','TG','PDAG', 'Schmidt_stability'])

g = 9.81 

dfs = []

# Loop for each WMO float :
for iWMO, WMO in enumerate(unique_WMO) :

    print(iWMO, WMO)

    WMO_profiles = df[df.PLATFORM_NUMBER == WMO] # Select all profiles for each argo float
    unique_cycles = WMO_profiles.CYCLE_NUMBER.unique() # Select all cycles for each argo float
    
    for jcycle, cycle in enumerate(unique_cycles) : 

        one_profile_data = WMO_profiles[WMO_profiles.CYCLE_NUMBER == cycle]
        
        # Discard profiles when there is a difference depth sign (depth decrease)
        depth_difference_init = one_profile_data['PRES'].iloc[1] - one_profile_data['PRES'].iloc[0] # initialization
        a = 0 # counter
        for p in range(1,len(one_profile_data['PRES'])-1) :
            depth_difference_new = one_profile_data['PRES'].iloc[p+1] - one_profile_data['PRES'].iloc[p]
            if np.sign(depth_difference_init) != np.sign(depth_difference_new) :
                a = a + 1 # discard profiles if a > 0

     
        # We calculate TG, SG, PDAG for each profile (need to avoid empty data) :
        # TG : temperature gradient
        # SG : salinity gradient
        # PDAG : potential density anomaly gradient
        
        if one_profile_data['TEMP'].size>1 and one_profile_data['PSAL'].size>1 and one_profile_data['PRES'].size>1 and one_profile_data['SIG0'].size>1 and np.isin(one_profile_data['TEMP_QC'], [1, 2]).all()==True and np.isin(one_profile_data['PSAL_QC'], [1, 2]).all()==True and a==0:

            TG    = np.gradient(one_profile_data['TEMP'],one_profile_data['PRES']) # Temperature gradient
            SG    = np.gradient(one_profile_data['PSAL'],one_profile_data['PRES']) # Salinity gradient
            PDAG  = np.gradient(one_profile_data['SIG0'],one_profile_data['PRES']) # PDA gradient
            SGT   = -0.01 # Salinity gradient threshold to detect surface saline lakes
            
            # Create a density column
            Density = np.zeros(np.shape(one_profile_data['PRES']))
            for m in range(len(one_profile_data['PRES'])):
                Density[m] = one_profile_data['SIG0'].iloc[m] + 1000

            '''
            # See the difference between both calculated densities
            fig, ax = plt.subplots(1,2,figsize=(7,7))
            # For both densities :
            ax[0].plot(one_profile_data['rho'], one_profile_data['PRES'],'m')
            ax[0].set_title('Rho in situ')
            ax[0].set_xlabel('Density in situ')
            ax[0].set_ylabel('Depth (m)')
            ax[0].grid()
            ax[0].invert_yaxis()

            ax[1].plot(Density, one_profile_data['PRES'],'c')
            ax[1].set_title('Density')
            ax[1].set_xlabel('Density')
            ax[1].set_ylabel('Depth (m)')
            ax[1].grid()
            ax[1].invert_yaxis()
            plt.savefig(os.path.join(directory, 'Argo_densities_%s_WMO_%s.png'%(cycle, WMO))) # save all the figures in the directory
            '''

            Year    = pd.DatetimeIndex(one_profile_data['TIME']).year
            Day     = pd.DatetimeIndex(one_profile_data['TIME']).day
            Month   = pd.DatetimeIndex(one_profile_data['TIME']).month
            
            # 3 conditions to detect surface saline lakes
            # Condition n°1 : Salinity gradient (SG) < -0.01 ppt/m
            # Condition n°2 : The salinity gradients above must not exceed 0.02 ppt/m (consistent definition of surface saline lake)
            # Condition n°3 : The surface salinity (the depth measured closest to the surface by the Argo float) must be higher than that at the base of the surface salt lake

            one_profile_data['SG_flag'] = [1 if SG[i] < SGT else 0 for i in range(one_profile_data.shape[0])]
            counter=one_profile_data['SG_flag'].sum()
            
            if counter >= 1 : # Condition n°1
                SG_min = np.nanmin(SG) # base of the saline lake
                SG_min_index = np.nanargmin(SG)
                depth_SG_min = one_profile_data['PRES'].iloc[SG_min_index]
                zd = depth_SG_min + 5
                index_zd = np.argmin([abs(i-zd) for i in one_profile_data['PRES']])

                s = 0 # Condition n°2
                for k in range(SG_min_index) :
                    if SG[k] > 0.02 :
                        s+=1 # Condition n°2 OK if s = 0 at the end of the loop
            
                min_salinity_between_depth_of_SG_min_and_zd = one_profile_data['PSAL'].iloc[SG_min_index] # initialization
                for o in range(SG_min_index, index_zd+1) :
                    if one_profile_data['PSAL'].iloc[o]<=min_salinity_between_depth_of_SG_min_and_zd :
                        min_salinity_between_depth_of_SG_min_and_zd = one_profile_data['PSAL'].iloc[0]
                
                t = 0 # Condition n°3
                if one_profile_data['PSAL'].iloc[0] <= min_salinity_between_depth_of_SG_min_and_zd :
                    t = 1 # Condition n°3 OK if t = 0

            if counter>=1 and s==0 and t==0 : # When Conditions 1, 2 and 3 are respected

                print('There is at least one gradient for cycle %s in WMO %d'%(cycle, WMO))
    
                SG_min       = np.nanmin(SG)
                SG_min_index = np.nanargmin(SG)
                depth_SG_min = one_profile_data['PRES'].iloc[SG_min_index]
                TG_val       = TG[SG_min_index]
                PDAG_val     = PDAG[SG_min_index]

                # Coordinates
                longitude    = one_profile_data['LONGITUDE'].iloc[SG_min_index]
                latitude     = one_profile_data['LATITUDE'].iloc[SG_min_index]
    
                # Time values 
                year   = int(Year[SG_min_index])
                day    = int(Day[SG_min_index])
                month  = int(Month[SG_min_index])

                # Schmidt Stability Index (SSI) calculation
                
                zd  = depth_SG_min + 5 # Saline lake depth (approximation) = zs
                z0  = one_profile_data['PRES'].iloc[0] 
                zg  = (zd - z0) / 2 

                index_zg = np.argmin([abs(i-zg) for i in one_profile_data['PRES']])
                density_g = one_profile_data['rho'].iloc[index_zg] # density value for depth = zg

                index_zd = np.argmin([abs(i-zd) for i in one_profile_data['PRES']])

                depth_water_column   = one_profile_data['PRES'][:index_zd+1].values
                density_water_column = one_profile_data['rho'].iloc[:index_zd+1]

                SSI = 0 

                for l in range(len(depth_water_column)-1):

                    z = depth_water_column[l]

                    index_z   = np.argmin([abs(i-z) for i in one_profile_data['PRES']])
                    density_z = one_profile_data['rho'].iloc[index_z] # We collect density value for depth = z

                    dz = one_profile_data['PRES'].iloc[l+1] - one_profile_data['PRES'].iloc[l] # prefer to use one_profile_data['PRES'] to avoid index issues
                
                    SSI = SSI + (z - zg)*(density_z - density_g)*dz

                    df_check_SSI_new_row = pd.DataFrame(data=np.array([[WMO, cycle, z0, zd, zg, z, density_g, density_z, dz, SSI]]), columns=['WMO', 'cycle', 'z0', 'zd', 'zg', 'z', 'density_g', 'density_z','dz','SSI'])
                    df_check_SSI = pd.concat([df_check_SSI, df_check_SSI_new_row], ignore_index=True)

                Schmidt_stability = g*SSI

                if Schmidt_stability > 0 :
                    
                    print('Schmidt_stability =', Schmidt_stability)

                    fig,ax=plt.subplots(2,3,figsize=(14,16))

                    ax[0, 0].plot(one_profile_data['TEMP'], one_profile_data['PRES'])
                    ax[0, 0].set_title('Temperature profile')
                    ax[0, 0].set_xlabel('Temperature (°C)')
                    ax[0, 0].set_ylabel('Depth (m)')
                    ax[0, 0].grid()
                    ax[0, 0].invert_yaxis()

                    ax[0, 1].plot(one_profile_data['PSAL'], one_profile_data['PRES'],'r')
                    ax[0, 1].set_title('Salinity profile')
                    ax[0, 1].set_xlabel('Salinity (ppt)')
                    ax[0, 1].set_ylabel('Depth (m)')
                    ax[0, 1].grid()
                    ax[0, 1].invert_yaxis()

                    ax[0, 2].plot(one_profile_data['SIG0'], one_profile_data['PRES'],'g')
                    ax[0, 2].set_title('PDA profile')
                    ax[0, 2].set_xlabel('PDA (kg/m^3)')
                    ax[0, 2].set_ylabel('Depth (m)')
                    ax[0, 2].grid()
                    ax[0, 2].invert_yaxis()

                    ax[1, 0].plot(TG, one_profile_data['PRES'])
                    ax[1, 0].set_title('Temperature gradient profile')
                    ax[1, 0].set_xlabel('Temperature gradient (°C/m)')
                    ax[1, 0].set_ylabel('Depth (m)')
                    ax[1, 0].grid()
                    ax[1, 0].invert_yaxis()

                    ax[1, 1].plot(SG, one_profile_data['PRES'], 'r')
                    ax[1, 1].set_title('Salinity gradient profile')
                    ax[1, 1].set_xlabel('Salinity gradient (ppt/m)')
                    ax[1, 1].set_ylabel('Depth (m)')
                    ax[1, 1].grid()
                    ax[1, 1].invert_yaxis()

                    ax[1, 2].plot(PDAG, one_profile_data['PRES'], 'g')
                    ax[1, 2].set_title('PDA gradient graph')
                    ax[1, 2].set_xlabel('PDA gradient (kg/m^3/m)')
                    ax[1, 2].set_ylabel('Depth (m)')
                    ax[1, 2].grid()
                    ax[1, 2].invert_yaxis()

                    plt.tight_layout(rect=[0, 0, 1, 0.95])
                    text1 = ('Schmidt_stability = ' + str(round(Schmidt_stability,2)) + ', z0 = ' + str(round(z0,2)) + ' m' + ', zd = ' + str(round(zd,2)) + ' m' + ', zg = ' + str(round(zg,2)) + ' m')
                    text2 = ('Saline lake depth = ' + str(depth_SG_min) + 'm' + ', SG_min = ' + str(round(SG_min,5)) + ' ppt/m' + ', TG = ' + str(round(TG_val,4)) + ' °C/m' + ', PDAG = ' + str(round(PDAG_val,2)) + ' kg/m^3/m')
                    combined_text = text1 + '\n' + text2

                    plt.figtext(0.5, -0.1, combined_text, wrap=True, horizontalalignment='center', fontsize=18)

                    plt.savefig(os.path.join(directory, '%s_%s_%s_%s_%s_%s_%s.png'%(WMO, cycle, round(latitude,3), round(longitude,3), day, month, year)), bbox_inches='tight') # save all the figures in the directory
                    plt.close('all')

                else :

                    SG_min = np.nan
                    depth_SG_min = np.nan
                    TG_val = np.nan
                    PDAG_val = np.nan
                    Schmidt_stability = np.nan
    
                    longitude = np.nan
                    latitude = np.nan
        
                    year = np.nan
                    day = np.nan
                    month = np.nan


            else :
                SG_min = np.nan
                depth_SG_min = np.nan
                TG_val = np.nan
                PDAG_val = np.nan
                Schmidt_stability = np.nan
    
                longitude = np.nan
                latitude = np.nan
    
                year = np.nan
                day = np.nan
                month = np.nan

            df_new_row = pd.DataFrame(data=np.array([[WMO, cycle, longitude, latitude, year, month, day, SG_min, depth_SG_min, TG_val, PDAG_val, Schmidt_stability]]), columns=['WMO', 'cycle', 'Longitude','Latitude','Year', 'Month', 'Day', 'SG_min','Depth','TG','PDAG', 'Schmidt_stability'])
            final_df = pd.concat([final_df,df_new_row], ignore_index=True)


final_df.to_csv(os.path.join(directory, "Save_variables.csv")) # Save surface saline lakes variables in a csv file
df_check_SSI.to_csv(os.path.join(directory, "Schmidt_stability_check.csv"), index=False)



