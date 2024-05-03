# Import the dependencies.
import numpy as np
from datetime import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api.v1.0/-startdate-<br/>"
        f"/api/v1.0/-startdate-/-enddate-<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    most_recent = session.query(measurement.date).order_by(measurement.date.desc()).first()
# Starting from the most recent data point in the database. 
    most_recent = dt(2017, 8, 23)
# Calculate the date one year from the last date in data set.
    desired_date = most_recent - dt.timedelta(days=365)

# Perform a query to retrieve the data and precipitation scores
    data = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= desired_date)
    precipitation_dict = {}
    #Put data into the dict
    for date, prcp in data:
        precipitation_dict[date] = prcp
    session.close()
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    #Query the station and the name
    station_query = session.query(station.station, station.name)
    station_list = []
    #Put the data into a list
    for stat, name in station_query:
        station_list.append(f"{stat} {name}")
    session.close()
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    #Making a date 1 year from last entry in dataset
    last_twelve = dt(2016, 8, 23)
    #Grabbing the temp data and date for a specific station but only the last year
    temp_query = session.query(measurement.tobs, measurement.date).filter(measurement.station == "USC00519281").filter(measurement.date > last_twelve)
    temp_list = []
    #Put the data into a list
    for temp, date in temp_query:
        temp_list.append(f"{temp} {date}")
    session.close()
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
def starter(start):
    session = Session(engine)
    #Converting input string to datetime format
    date_obj = dt.strptime(start, '%Y-%m-%d').date()
    start_date_list = [0,0,0]
    #Grabbing the min, max, and avg temp from start to end of dataset
    start_date_list[1]=session.query(func.max(measurement.tobs)).filter(measurement.date >= date_obj).scalar()
    start_date_list[0]=session.query(func.min(measurement.tobs)).filter(measurement.date >= date_obj).scalar()
    start_date_list[2]=session.query(func.avg(measurement.tobs)).filter(measurement.date >= date_obj).scalar()
    session.close()
    return jsonify(start_date_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
     #Converting input strings to datetime format
    date_obj_st = dt.strptime(start, '%Y-%m-%d').date()
    date_obj_end = dt.strptime(end, '%Y-%m-%d').date()
    start_end_date_list = [0,0,0]
     #Grabbing the min, max, and avg temp from start to end date
    start_end_date_list[1]=session.query(func.max(measurement.tobs)).filter(measurement.date >= date_obj_st).filter(measurement.date <= date_obj_end).scalar()
    start_end_date_list[0]=session.query(func.min(measurement.tobs)).filter(measurement.date >= date_obj_st).filter(measurement.date <= date_obj_end).scalar()
    start_end_date_list[2]=session.query(func.avg(measurement.tobs)).filter(measurement.date >= date_obj_st).filter(measurement.date <= date_obj_end).scalar()
    session.close()
    return jsonify(start_end_date_list)

if __name__ == '__main__':
    app.run(debug=True)