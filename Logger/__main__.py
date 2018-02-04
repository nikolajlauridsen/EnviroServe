from flask import Flask, request, g, make_response, jsonify, render_template, abort
from io import BytesIO
import sqlite3
import datetime
import time
import uuid


from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter

DATABASE = 'sensordata.db'
COLORS = {  # For plotting with matplot
    'red': (1, 0.012, 0.243),
    'green': (0, 0.502, 0),
    'blue': (0, 0.498, 1)
}

LoggerApi = Flask(__name__)


def make_dicts(cursor, row):
    """
    Converts database queries to dictionaries
    """
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


def get_db():
    """
    Opens database connection and returns database object
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = make_dicts
    return db


def init_db():
    """
    Initializes the database, creating all tables
    """
    with LoggerApi.app_context():
        db = get_db()
        with LoggerApi.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@LoggerApi.teardown_appcontext
def close_connection(exception):
    """
    Closes database connection
    """
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False, commit=False):
    """
    Query the database, if commit is False the function will fetch data
    if commit is true it'll insert data
    """
    db = get_db()

    try:
        cur = db.execute(query, args)
    except sqlite3.OperationalError:
        init_db()
        cur = db.execute(query, args)

    if commit:
        db.commit()
        cur.close()
        return None
    else:
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv


def extract_variables(expected_variables, _request):
    """
    Extract expected variables from a http request
    Will try both form and url parameters.
    :param expected_variables: List of expected variable names
    :param _request: Request to extract variables
    :return: Dictionary of extracted values and their names,
    sets None if no value is found, creates a list of both values if
    two different values is found for the same key name (form value first)
    """
    extracted_variables = {}
    for variable in expected_variables:
        form_var = _request.form.get(variable)
        args_var = _request.args.get(variable)
        if form_var and args_var:
            extracted_variables[variable] = [form_var, args_var]
        else:
            extracted_variables[variable] = form_var if form_var else args_var
    return extracted_variables


def query_climate_range(**kwargs):
    """
    Query the climate table for all data within a certain date range
    Is designed to work directly with extract variables where not all parameters are ensured.
    start time and end time is therefor both optional, if none is provided, all the data
    will be returned
    :param kwargs: start time and end time as kwargs
        start_time: start time as a unix time stamp
        end_time: end time as a unix time stamp
    :return:
    """
    if not kwargs['start_time']:
        kwargs['start_time'] = 0
    if not kwargs['end_time']:
        # Searching for data 1 day into the 'future' as a max limit seems fair.
        kwargs['end_time'] = time.time() + 24*3600

    if kwargs['sensor_id']:
        return query_db('SELECT * FROM climate WHERE ? < time < ? AND sensor_id = ?',
                        [kwargs['start_time'], kwargs['end_time'], kwargs['sensor_id']])
    else:
        return query_db('SELECT * FROM climate WHERE ? < time < ?',
                        [kwargs['start_time'], kwargs['end_time']])


@LoggerApi.route('/climate/data', methods=['GET', 'POST'])
def data():
    """
    Endpoint for inserting data into the climate table or retrieving all data
    from the climate table
    """
    if request.method == 'POST':
        params = extract_variables(['temp', 'humid', 'pressure',
                                    'time', 'sensor_id'], request)
        # Test to see if the minimum required variables were parsed
        if not (params['temp'] or params['humid'] or params['pressure'])\
                or not (params["time"] and params["sensor_id"]):
            # There's either no information or no sensor_id and time
            abort(400)

        try:
            # Try inserting values
            query_db('INSERT INTO climate VALUES (?, ?, ?, ?, ?)',
                     [params['temp'], params['humid'], params['pressure'],
                      params['time'], params["sensor_id"]], commit=True)
        except sqlite3.OperationalError:
            # Sensor not in database yet, add it with a temporary name
            query_db('INSERT INTO sensors VALUES (?, ?)',
                     [params["sensor_id"], uuid.uuid4()], commit=True)
            # Then insert values...
            query_db('INSERT INTO climate VALUES (?, ?, ?, ?, ?)',
                     [params['temp'], params['humid'], params['pressure'],
                      params['time'], params["sensor_id"]], commit=True)
            return 'Sensor added and data saved'
        return 'Data saved'
    elif request.method == 'GET':
        params = extract_variables(['start_time', 'end_time', 'sensor_id'], request)
        data = query_climate_range(**params)
        return jsonify(results=data)


@LoggerApi.route('/climate/now', methods=['GET'])
def now():
    """
    Endpoint for receiving the most recent entry in the climate table,
    useful for displaying the current-ish temperature
    """
    result = query_db('SELECT * FROM climate ORDER BY time DESC LIMIT 1;', one=True)
    return jsonify(result)


@LoggerApi.route('/climate/graph')
def graph():
    """
    Endpoint for generating a graph from the database
    Takes to optional form arguments
    start_time: UNIX timestamp
                earliest data point to retrieve
    end time: UNIX timestamp
              latest data point to retrieve
    """
    # Try to get params request
    params = extract_variables(['start_time', 'end_time'], request)
    # Fetch data from database
    results = query_climate_range(**params)

    # Turn it in to lists which can be graphed
    dates = []
    humids = []
    temps = []
    pressures = []
    for result in results:
        dates.append(datetime.datetime.fromtimestamp(result['time']))
        humids.append(result['humid'])
        temps.append(result['temp'])
        pressures.append(result['pressure'])

    # Graph it
    fig = Figure()
    # First y axis (temp and humid)
    axis = fig.add_subplot(1, 1, 1)
    # Plot humidity and temp on the same scale
    axis.plot_date(dates, humids, '-', color=COLORS['blue'])
    axis.plot_date(dates, temps, '-', color=COLORS['red'])
    axis.xaxis.set_major_formatter(DateFormatter('%d/%m/%y %H:%M'))
    axis.set_ylabel('Humidity in % & Temps in C')
    axis.set_xlabel('Time')
    # Second y axis (pressure)
    axis_pressure = axis.twinx()
    # Plot pressure
    axis_pressure.plot_date(dates, pressures, '-', color=COLORS['green'])
    axis_pressure.xaxis.set_major_formatter(DateFormatter('%d/%m/%y %H:%M'))
    axis_pressure.set_ylabel('Pressure in mbar')
    # Configure the figure
    fig.autofmt_xdate()
    fig.legend(['Humidity', 'Temperature', 'Pressure'], loc='lower right')
    fig.set_tight_layout(True)
    canvas = FigureCanvas(fig)
    # Save output
    png_output = BytesIO()
    canvas.print_png(png_output)

    # Create the response and send it
    response = make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response


@LoggerApi.route('/index')
def index():
    """
    Index page displaying last data set and graph
    """
    result = query_db('SELECT * FROM climate ORDER BY time DESC LIMIT 1;',
                      one=True)
    try:
        context = {'temp': round(result['temp'], 1),
                   'humid': round(result['humid'], 1),
                   'pressure': round(result['pressure']),
                   'time': datetime.datetime.fromtimestamp(int(result['time'])
                                                           ).strftime('%d-%m-%y %H:%M')}
    except TypeError:
        context = {'temp': None,
                   'humid': None,
                   'pressure': None,
                   'time': None}
    return render_template('index.html', **context)


if __name__ == '__main__':
    LoggerApi.run(host='0.0.0.0',
                  port=2020,
                  debug=True)
