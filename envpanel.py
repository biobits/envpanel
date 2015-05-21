from flask import Flask
from flask import render_template
from flask import g
import sqlite3
import json

import datetime


app = Flask(__name__)


#DATABASE = '/srv/data/PiShared/data/bighomedata.db'
DATABASE= 'F:/PiShared/PiShared/data/bighomedata.db'
#DATABASE = 'C:/DATA/PiShared/data/bighomedata.db'

# region DAL

def db_connect():
    return sqlite3.connect(DATABASE)


def connect_db(rfac):

    rv = sqlite3.connect(DATABASE)
    if rfac:
        rv.row_factory = sqlite3.Row
    return rv


def get_db(rfac):
    # db = getattr(g, '_database', None)
    # if db is None:
    #     db = g._database = connect_db(rfac)
    # return db
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db(rfac)
    return g.sqlite_db


# @app.teardown_appcontext
# def close_connection(exception):
#     db = getattr(g, '_database', None)
#     if db is not None:
#         db.close()

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def query_db(query, args=(), one=False,rfac=True):
    cur = get_db(rfac).execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv



def getMeasuresByLocationAndTimeRange(locid, startdate=datetime.datetime.now() - datetime.timedelta(days=1),
                                      enddate=datetime.datetime.now()):
    try:
        result=query_db('SELECT * from messwerte WHERE locationid=? and timestamp between ? and ?',
                        [locid, startdate, enddate],rfac=False)
    except Exception as e:
        result = -1
        raise e
    finally:
        return result

# region DAL end



# region BOL


def getMeasuresByLocation(idlocation):
    result=getMeasuresByLocationAndTimeRange(idlocation)
    return json.dumps(result)

def getLocations():
    result= query_db('select * from location',rfac=False)
    return  json.dumps(result)

def getOrte():
    result= query_db('select * from location')
    return result


# regin BOL end


# region APP

@app.route("/")
def index():
    _orte=getOrte()
    startort=3
    return render_template("starter.html", orte=_orte, startort=startort)

@app.route("/locations/<int:idloc>")
def location(idloc=3):

    return getMeasuresByLocation(idloc)


@app.route("/orte")
def orte():
    return getLocations()



if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)

# region APP end