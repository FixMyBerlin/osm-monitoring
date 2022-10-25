#Import necessary packages
import requests
import overpass
import datetime
import time
import os, sys
import logging

#Pfad für die heruntergeladenen Daten
path = "r:/[PFAD ZUM ORDNER]/RadnetzPlanungOSM/Data/OSMplus/"

#Logging
logging.basicConfig(filename='C:/OSM-RVP/Python/osm-rvp_01_query.log', filemode='a',level = logging.INFO,format='%(name)s - %(levelname)s - %(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')#, format='%(name)s - %(levelname)s - %(message)s'
logging.StreamHandler(sys.stdout)
#logging.debug('This is a debug message')
#logging.info('This is an info message')
#logging.warning('This is a warning message')
#logging.error('This is an error message')
#logging.critical('This is a critical message')

logging.info('Start with "osm_rvp_01_query_osm"')

#Begrenzung mit Koordinaten
s = 48.91
w = 9.00
n = 48.99
e = 9.17
bb = str(s) + ',' + str(w) + ',' + str(n) + ',' + str(e)
bb_out = str(s) + '-' + str(w) + '-' + str(n) + '-' + str(e)

#Check the date of the last successful query
files = [path+fn for fn in os.listdir(path) if "osm_relation" in fn]
dates=[]
for file in files:
    date = file[-14:-4]
    dates.append(datetime.datetime(int(date[:4]),int(date[5:7]),int(date[8:10]),0,0)) 
    
start = max(dates)+datetime.timedelta(days=1)
end = datetime.datetime.today() - datetime.timedelta(days = 1)

logging.info('Start date for query: '+ str(start))
logging.info('End date for query: '+ str(end))

#start = datetime.datetime(2022,7,26,0,0)
#end = datetime.datetime(2022,7,27,0,0)

#Definiere eine Liste mit Daten, zu welchen die OSM-Datenbank abgefragt werden soll\n",
def date_range(start, end):
    r = (end+datetime.timedelta(days=1)-start).days
    return [start+datetime.timedelta(days=i) for i in range(r)]

dates = date_range(start, end)


if not dates == []:

    logging.info('Start with the queries')

    #Make the connection to the overpass API
    api = overpass.API(timeout=60)

    #Loop the defined days and save data to disk
    for date in dates[:]:
        datum = '"'+date.isoformat()+'Z"'
        logging.info('Nächstes Datum: '+datum)
        
        query_node = """
        [timeout:900][maxsize:1073741824][date:"""+datum+"""];
        node("""+ bb +""");
        out geom meta;"""
        
        query_way = """
        [timeout:900][maxsize:1073741824][date:"""+datum+"""];
        way("""+bb+""");
        out geom meta;"""

        query_relation = """
        [timeout:900][maxsize:1073741824][date:"""+datum+"""];
        relation(""" + bb +""");
        out geom meta;"""

        while True:
            try:
                res = api.get(query_node, build=False)
                fname = 'osm_node_'+bb_out+'_'+datum[1:11]+'.dat'
                f = open(path+fname,"w")
                f.write(str(res.encode('utf-8')))
                f.close()
                
                logging.info(fname+' written to '+path)
                
                break
            except Exception as ex:
            
                logging.info(ex)
                time.sleep(10)
                
        while True:
            try:
                res = api.get(query_way, build=False)
                
                fname = 'osm_way_'+bb_out+'_'+datum[1:11]+'.dat'
                f = open(path+fname,"w")
                f.write(str(res.encode('utf-8')))
                f.close()
                
                logging.info(fname+' written to '+path)
                
                break
            except Exception as ex:
                logging.info(ex)
                time.sleep(10)
                    
        while True:
            try:
                res = api.get(query_relation, build=False)
                
                fname = 'osm_relation_'+bb_out+'_'+datum[1:11]+'.dat'
                f = open(path+fname,"w")
                f.write(str(res.encode('utf-8')))
                f.close()
                
                logging.info(fname+' written to '+path)
                
                break
            except Exception as ex:
                logging.info(ex)
                time.sleep(10)
                
else:
    logging.info('Data already downloaded. Exit')

logging.shutdown()     
