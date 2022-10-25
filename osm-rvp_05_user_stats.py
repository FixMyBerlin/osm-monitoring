import pandas as pd
import geopandas as gpd
import fiona

import datetime

import numpy as np

import datetime

import time, os, sys
import codecs

import logging

#Logging
logging.basicConfig(filename='C:/OSM-RVP/Python/osm-rvp_05_user_stats.log', filemode='a',level = logging.INFO,format='%(name)s - %(levelname)s - %(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')#, format='%(name)s - %(levelname)s - %(message)s'
logging.StreamHandler(sys.stdout)

logging.info('Start with "osm_rvp_05_user_stats"')


file_in = "r:/[PFAD ZUM ORDNER]/RadnetzPlanungOSM/Data/preprocessedPlus/osm_preproc_way.gpkg"
file_out = "r:/[PFAD ZUM ORDNER]/RadnetzPlanungOSM/Data/stats/stats_users.csv"



def date_range(start, end):
    r = (end+datetime.timedelta(days=1)-start).days
    return [start+datetime.timedelta(days=i) for i in range(r)]
    
    

start = datetime.datetime(2022,1,1,0,0)
end = datetime.datetime.today() - datetime.timedelta(days = 1)

dates = date_range(start, end)

#d = {'col1': [1, 2], 'col2': [3, 4]}
df = pd.DataFrame()


for date in dates[:]:
    
    layer = date.strftime('way_%Y-%m-%d')
    #print('Datum: ',datum)
    
    try:
        gdf    = gpd.read_file(file_in, layer=layer)
        
        #Data for user-stats
        anz_by_user = gdf.groupby('user').count().reset_index()
        anz_by_user = anz_by_user[['user','timestamp']].rename(columns={"timestamp": "count"})#.set_index('user')
        anz_by_user['date'] = date
        
        anz_by_user = anz_by_user.pivot(index='date',columns='user',values='count').reset_index()
        #print(anz_by_user['Peilscheibe','ghostrider44'])
        
        df = pd.concat([df, anz_by_user], ignore_index=True)
        
        #Data for tag-stats
        #anz_this_date = gdf.groupby('timestamp')
        
    except Exception as ex:
        print(ex)
        logging.error('Error reading/processing layer '+layer)
        

#Sort columns and save statistics to file

df2 = df.drop(['date'], axis=1)
df_sort = df2.max().sort_values(ascending=False)
df2 = df[['date']+df_sort.index.to_list()]

df2.to_csv(file_out,sep=';')

logging.info(file_out+' saved. Exit')
