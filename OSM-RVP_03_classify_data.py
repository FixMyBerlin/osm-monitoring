import pandas as pd
import geopandas as gpd

import numpy as np
import datetime
import time, os, sys
import codecs

import logging



#Logging
logging.basicConfig(filename='c:/Users/fc/workdir_op/osmrvp/osm-rvp_03_classify_data.log', filemode='a',level = logging.INFO,format='%(name)s - %(levelname)s - %(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')#, format='%(name)s - %(levelname)s - %(message)s'
logging.StreamHandler(sys.stdout)

logging.info('Start with "osm_rvp_03_classify_data"')



### Divide the data into the different classes
#### Use the classes provided by FixMyCity (https://github.com/FixMyBerlin/osm-scripts/tree/main/ZESPlus/Highways-BicycleWayData/filter)

# 1. Fahrradstraße (ggf. mit Zusatzzeichen)
# https://wiki.openstreetmap.org/wiki/DE:Key:bicycle%20road
#Eine ausschließlich für den Radverkehr vorgesehene Straße.
def fahrradstrasse(row):
    try:
        if (row.bicycle_road == 'yes') and (str(row.traffic_sign).startswith('DE:244')):
            return True
        else:
            return False
    except:
        return None

#gdf['osmrvp_fahrradstrasse'] = gdf.apply(lambda row:fahrradstrasse(row),axis = 1)
#gdf[gdf['osmrvp_fahrradstrasse']==True]

# 2. Fussgängerzone, Fahrrad erlaubt (ggf. mit Zusatzzeichen)
def strassefussgaengerzone(row):
    try:
        if (row.highway == 'pedestrian') and (row.bicycle == 'yes'):
            return True
        else:
            return False
    except:
        return None
    
#gdf['osmrvp_strassefussgaengerzone'] = gdf.apply(lambda row:strassefussgaengerzone(row),axis = 1)

# 3. / Gemeinsamer Geh- und Radweg
# traffic_sign=DE:240, https://wiki.openstreetmap.org/wiki/DE:Tag:traffic_sign%3DDE:240
# TODO: way/231469978 ist highway=cycleway, aber müsste vielleicht =path sein?

def radweggehweggemeinsam(row):
    try:
        if (((row.bicycle == 'designated') and (row.foot == 'designated') and (row.segregated == 'no')) or
            row.traffic_sign.startsWith("DE:240")):
            #Wenn schon als Fahrradstrasse klassifiziert, dann auslassen
            if row.osmrvp_fahrradstrasse !=True:
                return True
            else:
                return False
    except:
        return None

#gdf['osmrvp_radweggehweggemeinsam'] = gdf.apply(lambda row:radweggehweggemeinsam(row),axis = 1)
#gdf[gdf['osmrvp_radweggehweggemeinsam'] == True]

# 4. Getrennter Geh- und Radweg / Getrennter Rad- und Gehweg
# traffic_sign=DE:241-30, https://wiki.openstreetmap.org/wiki/DE:Tag:traffic_sign%3DDE:241-30
# traffic_sign=DE:241-31, https://wiki.openstreetmap.org/wiki/DE:Tag:traffic_sign%3DDE:241-31

def radweggehweggetrennt(row):
    
    try:
        if (((row.bicycle == 'designated') and (row.foot == 'designated') and (row.segregated == 'yes')) or
            (str(row.traffic_sign).startswith('DE:241'))):
            #  Wurde schon "Gemeinsamer Geh- und Radweg" klassifiziert, wird diese Klasse ignoriert
            if row.osmrvp_radweggehweggemeinsam !=True:
                return True
            else:
                return False
    except:
        return None

#gdf['osmrvp_radweggehweggetrennt'] = gdf.apply(lambda row:radweggehweggetrennt(row),axis = 1)
#gdf[gdf.osmrvp_radweggehweggetrennt == True]

### 5. Gehweg, Fahrrad frei
#### traffic_sign=DE:239,1022-10, https://wiki.openstreetmap.org/wiki/DE:Tag:traffic_sign%3DDE:239

def gehwegfahrradfrei(row):
    try:
        
        if ( ((row.highway in ['footway','path']) and (row.bicycle == 'yes')) or
            row['sidewalk_left_bicycle'] == 'yes' or
            row['sidewalk_right_bicycle'] == 'yes' or
            row['sidewalk_both_bicycle'] == 'yes' or #Note: kommt nicht in Excel vor
            ((row.traffic_sign == "DE:239,1022-10") and (row.highway != "cycleway")) #Note: kommt nicht in Excel vor
           ):
            if row.osmrvp_strassefussgaengerzone != True:
                return True
            else:
                return False
    except:
        return None

#gdf['gehwegfahrradfrei'] = gdf.apply(lambda row:gehwegfahrradfrei(row),axis = 1)
#gdf[gdf.gehwegfahrradfrei == True][['highway','bicycle']]


#  // The access based tagging would include free running path through woods
#  // like https://www.openstreetmap.org/way/23366687
#  // We filter those based on mtb:scale=*.
#  if (feature.properties["mtb:scale"]) return false


#gdf[gdf['mtb_scale'].notnull()]
#gdf[gdf['mtb_scale'] == None]

### 6. Radfahrstreifen, ein Radweg auf der Fahrbahn. Er wird durch einen durchgezogene oder gestrichelte Linie von der Fahrbahn abgeteilt.
#### https://wiki.openstreetmap.org/wiki/DE:Tag:cycleway%3Dlane
#### https://wiki.openstreetmap.org/wiki/DE:Tag:cycleway%3Dopposite_lane

def radfahrstreifen(row):
    try:
        
        if ( row.cycleway == 'lane' or         #Kommt nicht in Excel vor
            row.cycleway == 'opposite_lane' or #Kommt nicht in Excel vor
            row['cycleway_right'] == 'lane' or
            row['cycleway_left'] == 'lane' or
            row['cycleway_both'] == 'lane'
           ):
            return True
    except:
        return None

#gdf['radfahrstreifen'] = gdf.apply(lambda row:radfahrstreifen(row),axis = 1)
#gdf[gdf.radfahrstreifen == True][['highway','bicycle','cycleway','cycleway_right','cycleway_left','cycleway_both']]


### 7. Baulich abgesetzter Radweg
#### https://wiki.openstreetmap.org/wiki/DE:Tag:cycleway%3Dtrack
#### https://wiki.openstreetmap.org/wiki/DE:Tag:cycleway%3Dopposite_track
def baulichabgesetzterweg(row):
    try:
        
        if ( ((row.highway == 'cycleway') and (row.is_sidepath == 'yes')) or
            ((row.highway == 'cycleway') and (row.cycleway == 'crossing')) or
            ((row.traffic_signal == 'DE:237') and (row.is_sidepath == 'yes')) or
            ((row.cycleway == 'track') or (row.cycleway == 'opposite_track')) or
            ((row.cycleway_right == 'track') or (row.cycleway_left == 'track') or (row.cycleway_both == 'track'))
           ):        
            return True
    except:
        return None

### 9. // Small pieces of cycleway that are needed to create a routing network. (Kleine Radwegabschnitte, die zur Schaffung eines Routennetzes erforderlich sind)
#### We include them as a spearate category to stress their importance.
#### The example show a case where the biker needs to cross into traffic in an unsafe way.
#### Example:
####    https://www.openstreetmap.org/way/1013743829
####    https://www.mapillary.com/app/?lat=52.368165501442&lng=13.5959584918&z=17&focus=photo&pKey=850047429274697
#### Note, that this cannot catch all those connection ways, like https://www.openstreetmap.org/way/901972206,
####    which is categorized differently, but that is all we can do based on the signage (see pictures) and tagging.

def kleineradwegabschnitte(row):
    try:
        
        if ((row.highway == 'cycleway') and (row.geometry.length <= 15)):
            if row.baulichabgesetzterweg != True and row.radweggehweggemeinsam != True:
                return True
            else:
                return False
    except:
        return None

#gdf['kleineradwegabschnitte'] = gdf.apply(lambda row: kleineradwegabschnitte(row),axis = 1)
#gdf[gdf.kleineradwegabschnitte == True][['highway']]

### 8. // Dedicated and signed bicycle ways ( gewidmete und beschilderte Radwege)
#### - that are not parallel to a road - that are not connection pieces of a road
#### Eg. https://www.openstreetmap.org/way/27701956

def gewidmetebeschilderteradwege(row):
    try:
        
        if ( ((row.highway == 'cycleway') and (row.traffic_sign == 'DE:237') and not (row.is_sidepath == 'yes')) or
            ((row.highway in ['footway','path']) and (row.bicycle == 'yes') and (row.mtb_scale != np.nan) )
            
           ):        
            if row.kleineradwegabschnitte != True:
                return True
            else:
                return False
    except:
        return None

#gdf['gewidmetebeschilderteradwege'] = gdf.apply(lambda row: gewidmetebeschilderteradwege(row),axis = 1)
#gdf[gdf.gewidmetebeschilderteradwege == True][['highway','bicycle','cycleway','is_sidepath','mtb_scale']]

### 11. // Verkehrsberuhigter Bereich, umgangssprachlich auch „Spielstraße“
#### https://wiki.openstreetmap.org/wiki/DE:Tag:highway%3Dliving

def spielstrasse(row):
    try:
        
        if ((row.highway == 'living_street') and (row.bicycle != 'no')): #Nicht in Excel vorhanden
            return True
    except:
        return None

#gdf['spielstrasse'] = gdf.apply(lambda row: spielstrasse(row),axis = 1)
#gdf[gdf.spielstrasse == True][['highway']]


#Definiere eine Liste mit Daten, zu welchem die Statistik gemacht werden soll
def date_range(start, end):
    r = (end+datetime.timedelta(days=1)-start).days
    return [start+datetime.timedelta(days=i) for i in range(r)]




#Iterate through all topics. For each calculate the statistics for the different Radweg-Klassen
topics = ['way']#,'node']

for topic in topics:
    logging.info('Start mit: '+topic)
    
    file_stats = 'r:/PROZ_GL_Akquisition_VS/mFund/RadnetzPlanungOSM/Data/stats/stats_'+topic+'.csv'

    #Get last date in stats-file
    if os.path.exists(file_stats):
        stats = pd.read_csv(file_stats)
        lastdate_stats = stats['date'].max()
        lastdate_stats = datetime.datetime(int(lastdate_stats[:4]),int(lastdate_stats[5:7]),int(lastdate_stats[8:10]),0,0)
    else:
        lastdate_stats = datetime.datetime(2021,12,31,0,0)

    #start = datetime.datetime(2022,7,26,0,0)
    #end = datetime.datetime(2022,8,4,0,0)

    start = lastdate_stats+datetime.timedelta(days=1)
    end = datetime.datetime.today() - datetime.timedelta(days = 1)

    dates = date_range(start, end)

    file = "r:/PROZ_GL_Akquisition_VS/mFund/RadnetzPlanungOSM/Data/preprocessedPlus/osm_preproc_"+topic+".gpkg"

    stats = pd.DataFrame(columns = ['date','class','length','nelements'])

    for date in dates[:]:
    
        logging.info('Get stats for classes at '+str(date))
        
        layer = date.strftime(topic+'_%Y-%m-%d')
        #print('Datum: ',datum)
        
        try:
            gdf    = gpd.read_file(file, layer=layer)
        
            #Do classifications
            gdf['fahrradstrasse'] = gdf.apply(lambda row:fahrradstrasse(row),axis = 1)
            gdf['strassefussgaengerzone'] = gdf.apply(lambda row:strassefussgaengerzone(row),axis = 1)
            gdf['radweggehweggemeinsam'] = gdf.apply(lambda row:radweggehweggemeinsam(row),axis = 1)
            gdf['radweggehweggetrennt'] = gdf.apply(lambda row:radweggehweggetrennt(row),axis = 1)
            gdf['gehwegfahrradfrei'] = gdf.apply(lambda row:gehwegfahrradfrei(row),axis = 1)
            gdf['radfahrstreifen'] = gdf.apply(lambda row:radfahrstreifen(row),axis = 1)
            gdf['baulichabgesetzterweg'] = gdf.apply(lambda row:baulichabgesetzterweg(row),axis = 1)
            gdf['kleineradwegabschnitte'] = gdf.apply(lambda row: kleineradwegabschnitte(row),axis = 1)
            gdf['gewidmetebeschilderteradwege'] = gdf.apply(lambda row: gewidmetebeschilderteradwege(row),axis = 1)
            gdf['spielstrasse'] = gdf.apply(lambda row: spielstrasse(row),axis = 1)

            #Calculate nr of elements and length of ways per class
            length = [0]*10

            cols = ['fahrradstrasse','strassefussgaengerzone','radweggehweggemeinsam','radweggehweggetrennt','gehwegfahrradfrei','radfahrstreifen','baulichabgesetzterweg','kleineradwegabschnitte','gewidmetebeschilderteradwege','spielstrasse']
            for col in cols:
                length = gdf[gdf[col] == True].geometry.length.sum()
                nelements = len(gdf[gdf[col] == True].index)
                stats_col = pd.DataFrame({'date':[date],'class':[col],'length':[length],'nelements':[nelements]})
                stats= pd.concat([stats,stats_col])
                
        except Exception as ex:
            print(ex)
            

    #Append new statistics to stats-file
    stats.to_csv(file_stats,mode='a',header=False,index=False)
    
    logging.info(file_stats+' written. Exit')