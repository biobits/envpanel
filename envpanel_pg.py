from flask import Flask
from flask import render_template
from flask import g
import json
import datetime
import psycopg2
import psycopg2.extras
from json import JSONEncoder
app = Flask(__name__)

USR="user"
PWD="pass"
DATABASE="host=10.77.0.1 dbname=env_measures  user={} password={}".format(USR, PWD)

#region DAL


def connect_db():

    rv = psycopg2.connect(DATABASE)

    return rv


def get_db():
    # db = getattr(g, '_database', None)
    # if db is None:
    #     db = g._database = connect_db(rfac)
    # return db
    if not hasattr(g, 'pg_db'):
        g.pg_db = connect_db()
    return g.pg_db

##Json DateTime serialization
class DateEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()

        return JSONEncoder.default(self, obj)

# @app.teardown_appcontext
# def close_connection(exception):
#     db = getattr(g, '_database', None)
#     if db is not None:
#         db.close()

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'pg_db'):
        g.pg_db.close()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'pg_db'):
        g.pg_db.close()


def query_db(query, args=(), one=False, rfac=True):
    if rfac:
        cur = get_db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    else:
        cur = get_db().cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv



def getMeasuresByLocationAndTimeRange(locid, startdate=None, enddate=None):
    try:
        if startdate is None:
            startdate=datetime.datetime.now() - datetime.timedelta(days=1)

        if enddate is None:
            enddate=datetime.datetime.now()


        result=query_db('SELECT * from messwerte WHERE locationid=%s and timestamp between %s and %s',
                        [locid, startdate, enddate],rfac=False)
    except Exception as e:
        result = -1
        raise e
    finally:
        return result

#endregion



#region BOL


def getMeasuresByLocation(idlocation):
    result=getMeasuresByLocationAndTimeRange(idlocation)
    res=json.dumps(result,cls=DateEncoder)
    return res

def getLocations():
    result= query_db('select * from locations',rfac=False)
    res=json.dumps(result)
    return  res

def getOrte():
    result= query_db('select * from locations')
    return result


#endregion


#region APP

@app.route("/")
def index():
    _orte=getOrte()
    startort=3
    return render_template("starter.html", orte=_orte, startort=startort)

@app.route("/locations/<int:idloc>")
def location(idloc=None):
    if idloc is None:
        idloc=3

    return getMeasuresByLocation(idloc)


@app.route("/orte")
def orte():
    return getLocations()



if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=False)

#endregion