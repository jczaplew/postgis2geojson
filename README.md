# PostGIS2GeoJSON

## postgis2geojson.py

A simple tool for exporting from a PostGIS table to GeoJSON and TopoJSON. Assumes [Python 2.7+](http://www.python.org/download/), 
[psycopg2](http://initd.org/psycopg/download/), and [TopoJSON](https://github.com/mbostock/topojson/wiki/Installation) are already installed and in your PATH.

Adapted from Bryan McBride's excellent [PHP implementation](https://gist.github.com/bmcbride/1913855/).

####Example usage:

To export table "boundaries" from database "gisdata" as user "user" with password "password" to both GeoJSON and TopoJSON:

````python
python postgis2geojson.py -d gisdata -t boundaries -u user -p password --topojson
````

or, also specify that the geometry column is "the_geom", only fields "oid" and "name" should be returned, and the output file should be called "boundary_data":

````python 
python postgis2geojson.py -d gisdata -t boundaries -u user -p password -g the_geom -f oid name -o boundary_data --topojson
````

A full list of options is available via ````python postgis2geojson.py --help````.