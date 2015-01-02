import argparse
import datetime
import decimal
import json
import subprocess

import psycopg2


parser = argparse.ArgumentParser(
    description="Create a GeoJSON from a PostGIS query.",
    epilog="Example usage: python postgis2geojson.py -d awesomeData -h localhost -u user -p securePassword -t table -f id name geom -w 'columnA = columnB' -o myData --topojson")

parser.add_argument("-d", "--database", dest="database",
    type=str, required=True,
    help="The database to connect to")

# Python doesn't let you use -h as an option for some reason
parser.add_argument("-H", "--host", dest="host",
    default="localhost", type=str,
    help="Database host. Defaults to 'localhost'")

parser.add_argument("-u", "--user", dest="user",
    default="postgres", type=str,
    help="Database user. Defaults to 'postgres'")

parser.add_argument("-p", "--password", dest="password",
    default="", type=str,
    help="Password for the database user")

parser.add_argument("-P", "--port", dest="port",
    default="5432", type=str,
    help="Password for the database user")

parser.add_argument("-t", "--table", dest="table",
    type=str, required=True,
    help="Database table to query")

parser.add_argument("-f", "--fields", dest="fields",
    nargs="+",
    help="Fields to return separated by a single space. Defaults to *")

parser.add_argument("-g", "--geometry", dest="geometry",
    default="geom", type=str, 
    help="Name of the geometry column. Defaults to 'geom'")

parser.add_argument("-w", "--where", dest="where",
    type=str,
    help="Optional WHERE clause to add to the SQL query")

parser.add_argument("-o", "--output", dest="file",
    default="data", type=str,
    help="Output file name without extension. Defaults to 'data.geojson'")

parser.add_argument("--topojson", dest="topojson",
    action="store_true",
    help="Use if you would also like a copy of the data as TopoJSON")

parser.add_argument("--pretty", dest="pretty",
    action="store_true",
    help="Pretty print the output (indent).")

arguments = parser.parse_args()

# Fix to float decimals
# http://stackoverflow.com/questions/16957275/python-to-json-serialization-fails-on-decimal
def check_for_decimals(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError
    
def getData():
    # Connect to the database
    try:
        conn = psycopg2.connect("dbname=" + arguments.database + " user=" + arguments.user + " host=" + arguments.host + " port=" + arguments.port + " password="+ arguments.password)
    except:
        print "Unable to connect to the database. Please check your options and try again."
        return

    # Create a cursor for executing queries
    cur = conn.cursor()

    # Start building the query
    query = "SELECT "

    # If a list of fields were provided, add those
    if isinstance(arguments.fields, list):
        for each in arguments.fields:
            query += each + ", " 

    # Otherwise, just select everything
    else:
        query += "*, "

    query += "ST_AsGeoJSON(" + arguments.geometry + ") AS geometry FROM " + arguments.table

    # If a WHERE statement was provided, add that
    if arguments.where is not None:
        query += " WHERE " + arguments.where + ";"
    else:
        query += ";"

    # Execute the query
    try:
        cur.execute(query)
    except Exception as exc:
        print "Unable to execute query. Error was {0}".format(str(exc))
        return

    # Retrieve the results of the query
    rows = cur.fetchall()

    # Get the column names returned
    colnames = [desc[0] for desc in cur.description]

    # Find the index of the column that holds the geometry
    geomIndex = colnames.index("geometry")

    feature_collection = {'type': 'FeatureCollection', 'features': []}

    # For each row returned...
    for row in rows:
        feature = {
            'type': 'Feature',
            'geometry': json.loads(row[geomIndex]),
            'properties': {},
        }

        for index, colname in enumerate(colnames):
            if colname not in ('geometry', arguments.geometry):
                if isinstance(row[index], datetime.datetime):
                    # datetimes are not JSON.dumpable, manually stringify these.
                    value = str(row[index])
                else:
                    value = row[index]
                feature['properties'][colname] = value

        feature_collection['features'].append(feature)

    indent = 2 if arguments.pretty else None
    jsonified = json.dumps(feature_collection, indent=indent, default=check_for_decimals)

    # Write it to a file
    with open(arguments.file + '.geojson', 'w') as outfile:
        outfile.write(jsonified)

    # If a TopoJSON conversion is requested...
    if arguments.topojson is True:
        topojson()
    else:
        print "Done!"

def topojson():
    command = "topojson -o " + arguments.file + ".topojson -p -- " + arguments.file + ".geojson" 
    subprocess.call(command, shell=True)

# Start the process
getData()

