import sqlite3 as lite
import os

DATABASE = "sensordata.db"

# Fetch data from old database
con = lite.connect(DATABASE)
cur = con.cursor()
print('Fetching data from old database...')
cur.execute("SELECT * FROM climate")
data = cur.fetchall()
con.close()

# Create new database
print('Creating new database...')
new_db_con = lite.connect(DATABASE.rsplit('.')[0] + "_copy.db")
new_db_cur = new_db_con.cursor()
with open(os.path.join('Logger', 'schema.sql'), mode='r') as schema:
    new_db_cur.executescript("".join(schema.readlines()))
print('Database created...')

# Insert orignal sensor into sensor table.
print('Insert original sensor')
sensor_id = int(input("Desired sensor id: "))
sensor_name = input("Desire sensor name: ")
print('Inserting sensor...', end='')
new_db_cur.execute("INSERT INTO sensors VALUES (?, ?)", [sensor_id, sensor_name])
new_db_con.commit()
print(' Done!')

# Insert original data with the new sensor as it's parent
input('Press enter to start inserting old data...')
for datapoint in data:
    print('Inserting: ', datapoint)
    new_db_cur.execute("INSERT INTO climate VALUES (?, ?, ?, ?, ?)",
                       [datapoint[0], datapoint[1],
                        datapoint[2], datapoint[3],
                        sensor_id])
new_db_con.commit()
print('Done!')
