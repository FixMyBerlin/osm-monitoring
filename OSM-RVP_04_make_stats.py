import pandas as pd
#import geopandas as gpd

import numpy as np

import datetime
from dateutil.relativedelta import relativedelta

import time, os, sys
import codecs

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter 

import logging


file_stats = 'r:/[PFAD ZUM ORDNER]/RadnetzPlanungOSM/Data/stats/stats_way.csv'
file_plot = 'r:/[PFAD ZUM ORDNER]/RadnetzPlanungOSM/Data/stats/stats_way.jpg'


#Logging
logging.basicConfig(filename='C:/OSM-RVP/Python/osm-rvp_04_make_stats.log', filemode='a',level = logging.INFO,format='%(name)s - %(levelname)s - %(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')#, format='%(name)s - %(levelname)s - %(message)s'
logging.StreamHandler(sys.stdout)

logging.info('Start with "osm_rvp_04_make_stats"')


stats = pd.read_csv(file_stats)

#Create table for plotting       
statslen = pd.DataFrame(stats[stats["class"] == 'fahrradstrasse']['date'],columns = ['date'])
statsanz = pd.DataFrame(stats[stats["class"] == 'fahrradstrasse']['date'],columns = ['date'])

cols = ['fahrradstrasse','strassefussgaengerzone','radweggehweggemeinsam','radweggehweggetrennt','gehwegfahrradfrei','radfahrstreifen','baulichabgesetzterweg','kleineradwegabschnitte','gewidmetebeschilderteradwege','spielstrasse']
for col in cols:    
    statslen = pd.merge(statslen, stats[stats['class'] == col][['date','length']], on='date')
    statslen = statslen.rename(columns ={'length':col})
    
    statsanz = pd.merge(statsanz, stats[stats['class'] == col][['date','nelements']], on='date')
    statsanz = statsanz.rename(columns ={'nelements':col})

statslenrel = statslen.copy()
statsanzrel = statsanz.copy()


for col in cols:
    statslenrel[col]=statslenrel[col].astype(float) - float(statslenrel.iloc[0][col])
    statsanzrel[col]=statsanzrel[col].astype(float) - float(statsanzrel.iloc[0][col])
    
statslenrel.index = statslenrel['date']
statslenrel = statslenrel.apply(pd.to_numeric, errors='coerce')

statsanzrel.index = statsanzrel['date']
statsanzrel = statsanzrel.apply(pd.to_numeric, errors='coerce')

statslenrel['date'] = pd.to_datetime(statslenrel.index)
statsanzrel['date'] = pd.to_datetime(statsanzrel.index)




#Plot the data
cols_plot = ['Fahrradstrasse','Strasse Fussgängerzone','Radweg/Gehweg gemeinsam','Radweg/Gehweg getrennt','Gehweg - Fahrrad frei','Radfahrstreifen','Baulich abgesetzter Weg','Kleine Radwegabschnitte','Gewidmete beschilderte Radwege','Spielstrasse']


fig, axs = plt.subplots(2, 1)
fig.set_figheight(8)
fig.set_figwidth(8)

i = 0
for col in cols:
    axs[0].plot(statslenrel.date, statslenrel[col],label=cols_plot[i])
    axs[1].plot(statsanzrel.date, statsanzrel[col],label=cols_plot[i])
    i+=1
    
axs[0].set_xlabel('Datum')
axs[0].set_ylabel('Änderung Länge der Ways')
axs[1].set_xlabel('Datum')
axs[1].set_ylabel('Änderung Anzahl Ways')


# Define the date format
date_form = DateFormatter("%Y-%m")

datenow = datetime.datetime.now()
axs[0].xaxis.set_major_formatter(date_form)                                
axs[0].set_xlim([datenow - relativedelta(years=1), datenow])
axs[0].xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=7))
axs[1].set_xlim([datenow - relativedelta(years=1), datenow])
axs[1].xaxis.set_major_formatter(date_form)
axs[1].xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=7))
axs[0].legend(loc='upper left',bbox_to_anchor=(1,1))

#plt.rcParams['figure.figsize'] = [2, 4]

#Save plot as file
plt.tight_layout()
plt.savefig(file_plot)


logging.info(file_plot+' saved. Exit')
