from flask import Flask, request, g, make_response, jsonify
from io import BytesIO
import sqlite3
import datetime


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


@LoggerApi.route('/climate/data', methods=['GET', 'POST'])
def data():
    """
    Endpoint for inserting data into the climate table or retrieving all data
    from the climate table
    """
    if request.method == 'POST':
        query_db('INSERT INTO climate VALUES (?, ?, ?, ?)', [request.form['temp'],
                                                             request.form['humid'],
                                                             request.form['pressure'],
                                                             request.form['time']], commit=True)
        return 'Data saved'
    elif request.method == 'GET':
        data = query_db('SELECT * FROM climate')
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
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')

    # Fetch data from database
    if start_time and end_time:
        results = query_db('SELECT * FROM climate WHERE ? < time < ?', [start_time, end_time])
    elif start_time and not end_time:
        results = query_db('SELECT * FROM climate WHERE time > ?', [start_time])
    elif end_time and not start_time:
        results = query_db('SELECT * FROM climate WHERE time < ?', [end_time])
    else:
        results = query_db('SELECT * FROM climate')

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
    axis_pressure.set_ylabel('Pressure in millibar')
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


if __name__ == '__main__':
    LoggerApi.run(host='0.0.0.0',
                  port=2020,
                  debug=True)
