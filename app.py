import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, query
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
base = automap_base()
# reflect the tables
base.prepare(engine, reflect=True)

measurement = base.classes.measurement
Station = base.classes.station

url = 'http://127.0.0.1:5000'

session = Session(engine)

app = Flask(__name__)

@app.route("/")
def welcome():
    routes = (
    	f"<b>API routes:</b> <p>"
        f" <a href=" + url + "/api/v1.0/precipitation target='_blank'>" + "/api/v1.0/precipitation" + "</a> <p>"
        f" <a href=" + url + "/api/v1.0/stations target='_blank'>" + "/api/v1.0/stations" + "</a> <p>"
        f" <a href=" + url + "/api/v1.0/tobs target='_blank'>" + "/api/v1.0/tobs" + "</a> <p>"
        f" <a href=" + url + "/api/v1.0/YYYY-MM-DD target='_blank'>" + "/api/v1.0/YYYY-MM-DD" + "</a> <p>"
        f" <a href=" + url + "/api/v1.0/YYYY-MM-DD/YYYY-MM-DD target='_blank'>" + "/api/v1.0/YYYY-MM-DD/YYYY-MM-DD" + "</a> <p>"
        )
    return routes

@app.route("/api/v1.0/stations")
def station():
    print("stations list")

    session = Session(engine)

    station_query = session.query(Station.station, Station.name).all()

    station_data = {station:name for station,name in station_query}

    session.close()

    return jsonify(station_data)

@app.route("/api/v1.0/tobs")
def tobs():
    print("showing tobs")

    session = Session(engine)

    most_active_station = session.query(measurement.station, func.count(measurement.station)).\
        group_by(measurement.station).order_by(func.count(measurement.station).desc()).first()
    
    # last year of data (2016-08-23 to 2017-08-23)

    tobs_query = session.query(measurement.date, measurement.tobs).filter(measurement.date >= '2016-08-23').all()

    tobs_data = {date:tobs for date, tobs in tobs_query}

    return jsonify(tobs_data)

@app.route("/api/v1.0/precipitation")
def precipitation():
    print("showing precipitation")

    session = Session(engine)

    prcp_data = session.query(measurement.date, measurement.prcp).all()

    prcp_dict = {date:prcp for date, prcp in prcp_data}

    session.close()

    return jsonify(prcp_dict)

@app.route(f"/api/v1.0/<start_date>")
def startdatequery(start_date):
    print(f"showing start date of {start_date}")
    session = Session(engine)

    start = dt.datetime.strptime(start_date, '%Y-%m-%d')

    tmin = func.min(measurement.tobs)

    tmax = func.max(measurement.tobs)

    tavg = func.avg(measurement.tobs)

    query = session.query(tmin, tmax, tavg).filter(measurement.date >= start).all()

    session.close()

    return jsonify(query)

@app.route(f"/api/v1.0/<start_date>/<end_date>")
def startendquery(start_date = None, end_date = None):
	# print(f"showing start date of {start_date} and {end_date}")
    session = Session(engine)
    start_date = dt.datetime.strptime(start_date, '%Y-%m-%d')

    end_date = dt.datetime.strptime(end_date, '%Y-%m-%d')

    query = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
        filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()
    session.close()

    return jsonify(query)

if __name__ == '__main__':
    app.run(debug=True)