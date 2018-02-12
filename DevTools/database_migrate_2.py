import sqlite3 as lite
import os

DATABASE = "sensordata.db"

# Fetch data from old database
con = lite.connect(DATABASE)
cur = con.cursor()
print('Fetching sensors from old database...')
cur.execute("SELECT * FROM sensors;")
sensors = cur.fetchall()
print('Fetching data from old database...')
cur.execute("SELECT * FROM climate;")
data = cur.fetchall()
con.close()

# Create new database
print('Creating new database...')
new_db_con = lite.connect(DATABASE.rsplit('.')[0] + "_copy.db")
new_db_cur = new_db_con.cursor()
with open(os.path.join('Logger', 'schema.sql'), mode='r') as schema:
    new_db_cur.executescript("".join(schema.readlines()))
print('Database created...')

input('Press enter to start inserting old data...')
# Insert original sensors
print('Inserting sensors')
for sensor in sensors:
    print('Inserting: ', sensor)
    new_db_cur.execute("INSERT INTO sensors VALUES (?, ?)",
                       [sensor[0], sensor[1]])
new_db_con.commit()
print(' Done!')

# Insert original data with the new sensor as it's parent
print('Inserting climate data.')
for datapoint in data:
    print('Inserting: ', datapoint)
    new_db_cur.execute("INSERT INTO climate VALUES (?, ?, ?, ?, ?, ?, ?)",
                       [datapoint[0], datapoint[1],
                        datapoint[2], None, None, datapoint[3],
                        datapoint[4]])
new_db_con.commit()
print('Done!')


