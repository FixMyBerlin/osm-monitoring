import pandas as pd
import geopandas as gpd
import fiona
import osm2geojson
import numpy as np
import datetime
import time, os, sys
import codecs

import logging


#Paths
path_osm = "r:/[PFAD ZUM ORDNER]/RadnetzPlanungOSM/Data/OSMplus/"
path_preproc = "r:/[PFAD ZUM ORDNER]/RadnetzPlanungOSM/Data/preprocessedPlus/"
file_grenzen = "r:/[PFAD ZUM ORDNER]/RadnetzPlanungOSM/Data/GemeindegrenzenATKIS_BasisDLM/BietigheimBissingen.shp"

#Logging
logging.basicConfig(filename='C:/OSM-RVP/Python/osm-rvp_02_preprocess_data.log', filemode='a',level = logging.INFO,format='%(name)s - %(levelname)s - %(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')#, format='%(name)s - %(levelname)s - %(message)s'
logging.StreamHandler(sys.stdout)

logging.info('Start with "osm_rvp_02_preprocess_data"')

#Functions for the preprocessing
def filter_gdf(gdf):
    '''Filters the geodataframe to eliminate unwanted entries'''
    gdf = gdf.to_crs("epsg:25832")
    
    #kurzeGrundstuecksZufahrtenZugaenge
    gdf = gdf.query("~((highway  == 'service' or highway == 'footway') & (geometry.length <=10))")

    #Auch 'destination' raus, weil nicht teil der Infrastrutkur
    id_list = ['private','no','destination']
    gdf = gdf.query('access not in @id_list')
    
    #Grundstückszufahrten ignorieren
    gdf = gdf.query("~(service == 'driveway' or service == 'parking_aisle')")
    
    #Construction, Planned, Haltestellen, Flächen neben Schnellstraßen und Stufen ingnorieren
    id_list = ['construction','planned','proposed','platform','rest_area','steps']
    gdf = gdf.query('highway not in @id_list')
    
    #Weitere highway-values, welche ignoriert werden sollen
    id_list = ['street_lamp','bus_stop','traffic_signals','give_way','passing_place','stop','elevator',
               'emergency_access_point','turning_loop','raceway','milestone','speed_camera','corridor','mini_roundabout']
    gdf = gdf.query('highway not in @id_list')
        
    return gdf


def filter_gemeinde(gdf, grenzen):
    '''Filters to the geographic area of the Gemeinde'''
    gdf = gdf.to_crs('EPSG:25832')
    gdf_bb = gpd.sjoin(gdf, grenzen)
    return gdf_bb
    

def getit(row,col):
    try:
        return row.get(col)
    except:
        return np.nan


def make_gdf(geojson, grenzen):
    '''Creates a geopandas dataframe out of the geojson and filters for bike-relevant tags'''
    #### Make a geopandas geodataframe from 
    gdf = gpd.GeoDataFrame.from_features(geojson)
    gdf.crs = "EPSG:4326"
    
    #Filter data inside community
    gdf = filter_gemeinde(gdf, grenzen)
    
    #Extract all necessary keys
    cols = ['highway','bicycle','foot','segregated','bicycle_road','traffic_sign','sidewalk:left:bicycle','sidewalk:right:bicycle','sidewalk:both:bicycle','cycleway','cycleway:left','cycleway:right','cycleway:both','traffic_signal','is_sidepath','cycleway:right','cycleway:left','cycleway:both','mtb_scale','access','service']
    for col in cols:
        gdf[col] = gdf['tags'].apply(lambda x: getit(x,col))

    #Filter for only lines that contain valuable information for bikes
    subset = ['bicycle','foot','segregated','bicycle_road','traffic_sign','sidewalk:left:bicycle','sidewalk:right:bicycle','sidewalk:both:bicycle','cycleway','cycleway:left','cycleway:right','cycleway:both','traffic_signal','is_sidepath','mtb_scale']
    gdf = gdf.dropna(subset=subset, how = 'all').reset_index()
    
    #### Replace unwanted characters in column names and insert missing columns
    gdf.columns = gdf.columns.str.replace(":", "_")

    names = ['highway','bicycle','foot','segregated','bicycle_road','traffic_sign','sidewalk_left_bicycle','sidewalk_right_bicycle','sidewalk_both_bicycle','cycleway','cycleway_left','cycleway_right','cycleway_both','traffic_signal','is_sidepath','mtb_scale','access','service']
    for name in names:
        if not name in gdf.columns:
            gdf[name] = np.nan

    #Filter irrelevant data
    gdf = filter_gdf(gdf)
    
    #Remove unused columns
    cols = names = ['timestamp', 'user', 'uid','version','highway','bicycle','foot','segregated','bicycle_road','traffic_sign','sidewalk_left_bicycle','sidewalk_right_bicycle','sidewalk_both_bicycle','cycleway','cycleway_left','cycleway_right','cycleway_both','traffic_signal','is_sidepath','mtb_scale','geometry']
    gdf = gdf[cols]
    return gdf
    


#Make lists of files to process
files_node = [path_osm+fn for fn in os.listdir(path_osm) if "osm_node" in fn]
files_way = [path_osm+fn for fn in os.listdir(path_osm) if "osm_way" in fn]
files_relation = [path_osm+fn for fn in os.listdir(path_osm) if "osm_relation" in fn]

#Get the boundary of the Gemeinde
grenzen = gpd.read_file(file_grenzen)

#Go through all files and preprocess them

topics = ['way','node','relation']
topics = ['way','node']

for topic in topics:
    logging.info('Start mit: '+topic)
    
    #Set the topic
    if topic == 'node':
        files = files_node
    if topic == 'way':
        files = files_way
    if topic == 'relation':
        files = files_relation
        
    #Check last layer in Geopackage
    file_preproc = path_preproc+"osm_preproc_"+topic+".gpkg"
    print(file_preproc)
    
    #Get last date in geopackage
    try:
        layers = fiona.listlayers(file_preproc)
        dates=[]
        for layer in layers:
            date = layer[-10:]
            dates.append(datetime.datetime(int(date[:4]),int(date[5:7]),int(date[8:10]),0,0)) 
        
        lastdate_geopackage = max(dates)
    except:
        lastdate_geopackage = datetime.datetime(2021,12,31,0,0)
  

    #Get last date of downloaded files
    dates=[]
    for count, file in enumerate(sorted(files)):
        date = file[-14:-4]
        dates.append(datetime.datetime(int(date[:4]),int(date[5:7]),int(date[8:10]),0,0))

        if dates[-1] == lastdate_geopackage:
            pos = count
    lastdate_files = max(dates)
   

    #Filter the lists of files to the last dates than were not yes included in the geopackage
    if lastdate_files >= lastdate_geopackage:    
        files = files[pos+1:]
    
    #Now start preprocessing all new files for this topic
    for file in files:
    
        logging.info('Preprocess: '+file)

        ### Convert XML to Geojson
        with codecs.open(file, 'r') as data:#,encoding='cp1252' utf-8
            
            try:
                xml = data.read()
                xml2 = xml[:-1].replace('b\'','')
                xml2 = xml2.replace('\\n','')
            except ex as Exception:
                logging.error(ex)

            #Convert xml to geojson
            try:
                geojson = osm2geojson.xml2geojson(xml2, filter_used_refs=False, log_level='ERROR')
            except ex as Exception:
                logging.error(ex)

            #Convert geojson to Geopandas dataframe and filter the data
            try:
                gdf = make_gdf(geojson, grenzen)  
            except ex as Exception:
                logging.error(ex)
            
            #In Geopackage SQL-lite-Datenbank herausschreiben
            try:
                gdf = gpd.GeoDataFrame(gdf,crs = 'EPSG:25832',geometry = gdf.geometry)
                gdf.to_file(path_preproc+"osm_preproc_"+topic+".gpkg",layer=topic+'_'+file[-14:-4])
            except ex as Exception:
                logging.error(ex)















