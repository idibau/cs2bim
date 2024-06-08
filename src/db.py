import psycopg2

from wkt2tin.polygon import Area

conn = psycopg2.connect(
    "dbname = 'cs2bim' user = 'postgres' host = 'host.docker.internal' password = 'postgres'"
)
cur = conn.cursor()

# count rows in the table
cur.execute("select ST_AsText(ST_CurveToLine(geometrie)) from cs2bim.liegenschaft")
result = cur.fetchone()
print(result)

if result is not None:  
    area = Area(result[0])
    print ("Test")