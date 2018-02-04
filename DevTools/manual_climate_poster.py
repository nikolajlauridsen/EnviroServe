"""
Quick and dirty script to inject datapoints into the databse
for test purposes
"""
import requests
import time

URL = 'http://127.0.0.1:2020/climate/data'


payload = {"temp": None,
           "humid": None,
           "pressure": None,
           "time": None,
           "sensor_id": None}

print('Input injector'.center(40, '~'))
print('Enter 0 or empty string, for no value')
print('When inputting time, -1 will input now\n')

for key in payload.keys():
    payload[key] = input('Input {}: '.format(key))
    # Revert back to none if the answer was 0
    if payload[key] == "0" or payload[key] == "":
        payload[key] = None

if payload["time"] == "-1":
    payload["time"] = time.time()

print('\nCurrent payload:\n{}'.format(payload))
input('Last chance to ctrl-c')

print('Sending request...', end='')
res = requests.post(URL, data=payload)
print('Done!')
print('Status code: {}\nContent:\n{}'.format(res.status_code, res.content))
