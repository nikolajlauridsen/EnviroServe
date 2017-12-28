import requests
from requests.exceptions import InvalidURL
import json
import sys
import datetime


def convert_unix(unix_stamp, _format):
    """Convert a unix timestamp to a time string"""
    return datetime.datetime.fromtimestamp(unix_stamp).strftime(_format)


API_IP = "192.168.1.250"
API_PORT = "2020"

if __name__ == '__main__':
    print('Requesting data from API...')
    try:
        res = requests.get('http://{}:{}/climate/now'.format(API_IP, API_PORT), timeout=10)
        res.raise_for_status()
    except InvalidURL:
        sys.exit('Invalid URL, most likely a problem with the API_IP or API_PORT constants in __main__.py')
    except Exception as e:
        print('Something went wrong when connecting to API...')
        raise e

    data = json.loads(res.text)
    print('\n{}: {}\'C | {}% | {} millibars'.format(convert_unix(data['time'], '%d/%m/%Y %H:%M:%S'),
                                                    round(data['temp'], 1),
                                                    round(data['humid'], 1),
                                                    round(data['pressure'], 1)))
