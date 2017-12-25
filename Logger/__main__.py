from flask import Flask, request, g, make_response, jsonify
import sqlite3

DATABASE = 'sensordata.db'


LoggerApi = Flask(__name__)


def make_dicts(cursor, row):
    """Converts database queries to dictionaries"""
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


def get_db():
    """Opens database connection and returns database object"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = make_dicts
    return db


def init_db():
    """Initializes the database, creating all tables"""
    with LoggerApi.app_context():
        db = get_db()
        with LoggerApi.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@LoggerApi.teardown_appcontext
def close_connection(exception):
    """Closes database connection"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False, commit=False):
    """Query the database, if commit is False the function will fetch data
    if commit is true it'll insert data"""
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
    if request.method == 'POST':
        query_db('INSERT INTO climate VALUES (?, ?, ?, ?)', [request.form['temp'],
                                                             request.form['humid'],
                                                             request.form['pressure'],
                                                             request.form['time']], commit=True)
        return 'Data saved'
    elif request.method == 'GET':
        data = query_db('SELECT * FROM climate')
        return jsonify(results=data)


if __name__ == '__main__':
    LoggerApi.run(host='0.0.0.0',
                  port=2020,
                  debug=True)