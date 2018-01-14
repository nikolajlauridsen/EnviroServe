from sense_hat import SenseHat, DIRECTION_UP, DIRECTION_DOWN, DIRECTION_RIGHT, ACTION_PRESSED
import time
import requests
from requests import ConnectionError, Timeout

RESOLUTION = 60*5      # How often to report in on environmental stats.
HUMID_WARN = 60        # Humidity to warn at.
HUMID_PAUSE = 60*30   # How long to wait after humid warning is dismissed.

LOGGER_IP = "0.0.0.0"
LOGGER_PORT = "2020"

# ------------ LED list for warning sign ------------
# Colors
X = [255, 0, 0]    # Red
Y = [0, 191, 255]  # Bright blue
O = [250, 255, 0]  # Bright yellow

# LED matrix layout
WARNING_SIGN = [
    O, O, O, O, O, O, O, O,
    O, O, O, X, O, O, O, O,
    O, O, X, Y, X, O, O, O,
    O, X, O, Y, O, X, O, O,
    X, O, O, O, O, O, X, O,
    X, O, O, Y, O, O, O, X,
    X, X, X, X, X, X, X, X,
    O, O, O, O, O, O, O, O
]
# ------------ LED list for warning sign ------------


def get_data(sense):
    data = {"temp": sense.get_temperature(),
            "humid": sense.get_humidity(),
            "pressure": sense.get_pressure(),
            "time": time.time()}
    return data


def send_data(_data):
    try:
        res = requests.post('http://{}:{}/climate/data'.format(LOGGER_IP,
                                                               LOGGER_PORT),
                            data=_data, timeout=20)

        res.raise_for_status()
        print(res.text)
    except Timeout:
        print('API timed out..')
    except ConnectionError:
        print('Couldn\'t connect to server, skipping reporting to API...')


def init_sense():
    """
    Initialize the sense hat
    """
    sense = SenseHat()
    sense.clear()
    sense.set_rotation(180)  # I'm using my sense hat upside down
    sense.low_light = True   # This thing is very, very bright
    return sense


if __name__ == '__main__':
    print('Setting up Sense HAT')
    sense = init_sense()
    print('Starting main loop.')

    last_check = 0
    last_warn = 0
    night_mode = False

    while True:
        # Handle joystick events
        for event in sense.stick.get_events():
            print('Event received:\n{}'.format(event))
            if event.direction == DIRECTION_UP and event.action == ACTION_PRESSED:
                data = get_data(sense)
                if data['humid'] > HUMID_WARN:
                    sense.show_message('{}%! Open a window!!'.format(round(data['humid'])),
                                       text_colour=[255, 0, 0], back_colour=[200, 255, 0])
                    sense.clear()
                else:
                    sense.show_message("{}'C {}%".format(round(data['temp']),
                                                         round(data['humid'])), text_colour=[128, 0, 0])
            elif event.direction == DIRECTION_DOWN and event.action == ACTION_PRESSED:
                print('Clearing LEDs')
                sense.clear()
            elif event.direction == DIRECTION_RIGHT and event.action == ACTION_PRESSED:
                if night_mode:
                    print('Disabling night mode')
                    sense.show_message('Disabling night mode. Good morning sunshine!', text_colour=O)
                    night_mode = False
                    sense.clear()
                else:
                    print('Enabling night mode')
                    sense.show_message('Enabling night mode, good night', text_colour=[0, 0, 100])
                    night_mode = True
                    sense.clear()

        # Periodically check the stats
        if time.time() - last_check > RESOLUTION:
            data = get_data(sense)
            print('Checking sensors: {}\'C, {}%, Pres. {} Millibars'.format(round(data['temp']),
                                                                            round(data['humid']),
                                                                            round(data['pressure'])))
            print('Sending data')
            send_data(data)
            if data['humid'] > HUMID_WARN and data["time"] - last_warn > HUMID_PAUSE and not night_mode:
                print('Triggering warning')
                sense.set_pixels(WARNING_SIGN)
                time.sleep(0.5)
                sense.show_message('Humidity warning {}%'.format(round(data['humid'])),
                                   back_colour=O, text_colour=[255, 0, 0])
                sense.set_pixels(WARNING_SIGN)
                last_warn = data["time"]
            last_check = data["time"]

        # No reason to use more resources than needed
        time.sleep(1)
