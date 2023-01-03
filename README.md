# OSM-Monitoring

Automatische Auswertung von Fahrradinfrastruktur von OpenStreetMap Daten.

## Installation for Windows 

1. Install python in User folder
Download Python | Python.org: https://www.python.org/downloads/
Version darf nicht aktueller sein, als die vorhandenen Wheels für GDAL und FIONA (siehe Links unten)

2. Set up environment
Im cmd-Fenster:
```
py -m pip install --upgrade pip setuptools wheel
py -m venv osmrvp100
osmrvp100\Scripts\activate
```

3. Installation der benötigten Python packages

In der neu geschaffenen Umgebung osmrvp100:
```
py -m pip install requests
py -m pip install overpass
py -m pip install pandas


py -m pip install c:\Users\[USER]\AppData\Local\Programs\Python\wheels\GDAL-3.4.3-cp310-cp310-win_amd64.whl
```
--> das Wheel-File vorher hier [Archived: Python Extension Packages for Windows - Christoph Gohlke (uci.edu)](https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal) runteladen

```
py -m pip install c:\Users\[USER]\AppData\Local\Programs\Python\wheels\Fiona-1.8.21-cp310-cp310-win_amd64.whl
```
--> Das Wheel-File vorher hier [Archived: Python Extension Packages for Windows - Christoph Gohlke (uci.edu)](https://www.lfd.uci.edu/~gohlke/pythonlibs/#fiona) runterladen

```
py -m pip install geopandas
```
--> funktioniert nur, wenn vorher GDAL und FIONA installiert wurden

```
py -m pip install osm2geojson
py -m pip install datetime
py -m pip install openapi-codec
py -m pip install matplotlib
py -m pip install rtree
pip install github
py -m pip install notebook
```
## Installation for Linux

Use `requirements.txt` for installation of all pip packages:
```sh
pip install -r requirements.txt
```

## 4. Nutzung der Umgebung:
Im cmd-Fenster und im entsprechenden Ordner:
```
osmrvp100\Scripts\activate
py -m meinskript.py
```
Start jupyter notebook:
```
py -m notebook
```

# License

This code is licensed under AGPL-3.0 license.