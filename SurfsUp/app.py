import pandas as pd
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import flask
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite", pool_pre_ping=True)

Base = automap_base()
Base.prepare(engine, reflect=True)

measurement = Base.classes.measurement
station = Base.classes.station

session = Session(engine)

app = Flask(__name__)

@app.route("/")
def welcome():
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    year_from = dt.date(2017,8,23) - dt.timedelta(days=365)

    annual_prcp = session.query(measurement.date, measurement.prcp).filter(measurement.date >= year_from, measurement.prcp != None).order_by(measurement.date).all()
    return jsonify(dict(annual_prcp))

@app.route("/api/v1.0/stations")
def stations():
    session.query(measurement.station).distinct().count()
    active_stations = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    return jsonify(dict(active_stations))

@app.route("/api/v1.0/tobs")
def tobs():
    tobss = session.query(measurement.tobs).filter(measurement.station == 'USC00519281').filter(measurement.date >= '2017,8,23').all()
    tobs_list = list(np.ravel(tobss))
    return jsonify(tobs_list)

def calc_start(start_date):
    return session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    
@app.route("/api/v1.0/<start>")
def start_date(start):
    calc_start = calc_start(start)
    start_temp = list(np.ravel(calc_start))

    temp_min = start_temp[0]
    temp_max = start_temp[1]
    temp_avg = start_temp[2]
    temp_dict = {"Minimum Temperature": temp_min, "Maximum Temperature": temp_max, "Average Temperature": temp_avg}
    return jsonify(temp_dict)

def calc_temps(start_date, end_date):
    return session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= start_date).filter(measurement.date <= end_date.all())

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    calc_temp = calc_temps(start, end)
    ta_temp = list(np.ravel(calc_temp))

    t_min = ta_temp[0]
    t_max = ta_temp[1]
    t_avg = ta_temp[2]
    temp_dict2 = {"Minimum Temperature": t_min, "Maximum Temperature": t_max, "Average Temperature": t_avg}
    return jsonify(temp_dict2)

if __name__ == "__main__":
    app.run(debug=True)