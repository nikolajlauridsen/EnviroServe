import requests
from requests.exceptions import InvalidURL
import json
import sys
import datetime
import argparse
from PIL import Image
import time


def convert_unix(unix_stamp, _format):
    """Convert a unix timestamp to a time string"""
    return datetime.datetime.fromtimestamp(unix_stamp).strftime(_format)


def get_newest_data():
    """
    Request the most recent data set from the api
    :return: dictionary with temp, humid, pressure and time
    """
    try:
        res = requests.get('http://{}:{}/climate/now'.format(API_IP, API_PORT),
                           timeout=10)
        res.raise_for_status()
    except InvalidURL:
        sys.exit('Invalid URL, most likely a problem with the API_IP or '
                 'API_PORT constants in __main__.py')
    except Exception as e:
        print('Something went wrong when connecting to API...')
        raise e

    return json.loads(res.text)


def get_graph(start):
    try:
        res = requests.get('http://{}:{}/climate/graph'.format(API_IP, API_PORT),
                           timeout=10, data={'start_time': start}, stream=True)
        res.raise_for_status()
    except InvalidURL:
        sys.exit('Invalid URL, most likely a problem with the API_IP or '
                 'API_PORT constants in __main__.py')
    except Exception as e:
        print('Something went wrong when connecting to API...')
        raise e

    image_file = Image.open(res.raw)
    return image_file


API_IP = "192.168.1.250"
API_PORT = "2020"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get info from EnviroSense')
    parser.add_argument('-d', '--days', type=float, default=None)
    parser.add_argument('-hr', '--hours', type=float, default=None)
    args = parser.parse_args()

    if args.days or args.hours:
        if args.hours and not args.days:
            print('Fetching graph for the last {} hours'.format(args.hours))
            start_time = time.time() - (args.hours * 3600)
        elif args.days and not args.hours:
            print('Fetching graph for the last {} days'.format(args.days))
            start_time = time.time() - (args.days * 24 * 3600)
        else:
            print('Fetching graph for the last {} days and {} hours'
                  ''.format(args.days, args.hours))
            start_time = time.time() - (args.days*24*3600 + args.hours*3600)
        image = get_graph(start_time)
        image.show()
    else:
        print('Requesting data from API...')
        data = get_newest_data()
        print('\n{}: {}\'C | {}% | {} millibars'.format(convert_unix(data['time'], '%d/%m/%Y %H:%M:%S'),
                                                        round(data['temp'], 1),
                                                        round(data['humid'], 1),
                                                        round(data['pressure'], 1)))
