# TODO: Put this in a proper config file
RESOLUTION = 60*2     # How often to report in on environmental stats.
HUMID_WARN = 70        # Humidity to warn at.
HUMID_PAUSE = 60*30   # How long to wait after humid warning is dismissed.
SENSOR_ID = 1         # Unique ID for this sensor, allows us to have multiple
                      # sensors reporting back to the same "brain"

LOGGER_IP = "0.0.0.0"
LOGGER_PORT = "2020"
