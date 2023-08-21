# Import the dependencies.

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as datetime
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

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
        f"/api/v1.0/start_date(YYYY-MM-DD)<br/>"
        f"/api/v1.0/start_date(YYYY-MM-DD)/end_date(YYYY-MM-DD)"
    )

#################################################

@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)
   
    # Query all precipitation - last 12 months data
    results = session.query(Measurement.date, Measurement.prcp).\
                        filter(Measurement.date >= '2016-08-23').\
                        filter(Measurement.date <= '2017-08-23').\
                        order_by(Measurement.date).all()

    session.close()

    # Create a dictionary using date as the key and prcp as the value
    precipitation_data = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["Date"] = date
        precipitation_dict["Precipitation"] = prcp
        precipitation_data.append(precipitation_dict) 

    return jsonify(precipitation_data)  

#################################################

@app.route("/api/v1.0/stations")
def stations():

    # Query for list of stations from dataset
    results = session.query(Station).all()

    session.close()

    station_data = []
    for station in results:
        station_dict = {}
        station_dict["Station"] = station.station
        station_dict["Name of Station"] = station.name
        station_data.append(station_dict)

    return jsonify(station_data)  

#################################################

@app.route("/api/v1.0/tobs")
def tobs():

    # Query the dates and temperature observations of the most-active station for the previous year of data
    results = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.station == 'USC00519281').\
                filter(Measurement.date >= '2016-08-23').all()

    session.close()

    temp_data = []
    for date, tobs in results:
        temp_dict = {}
        temp_dict["Date"] = date
        temp_dict["Temperature"] = tobs
        temp_data.append(temp_dict)

    return jsonify(temp_data)   

#################################################

@app.route("/api/v1.0/<start>")
def start_date(start):

    start_date = datetime.datetime.strptime(start, '%Y-%m-%d').date()
    temperature_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    temps_stats_results = list(np.ravel(temperature_stats))

    min_temp = temps_stats_results[0]
    max_temp = temps_stats_results[1]
    avg_temp = temps_stats_results[2]    

    temp_stats_data= []
    temp_stats_dict = [{"Start Date": start},
                       {"TMIN": min_temp},
                       {"TMAX": max_temp},
                       {"TAVG": avg_temp}]

    temp_stats_data.append(temp_stats_dict)

    return jsonify(temp_stats_data)     


#################################################

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):

    start_date = datetime.datetime.strptime(start, '%Y-%m-%d').date()
    end_date = datetime.datetime.strptime(end, '%Y-%m-%d').date()

    temperature_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    temps_stats_results = list(np.ravel(temperature_stats))

    min_temp = temps_stats_results[0]
    max_temp = temps_stats_results[1]
    avg_temp = temps_stats_results[2]


    temp_stats_data = []
    temp_stats_dict = [{"Start Date": start_date},
                       {"End Date": end_date},
                       {"TMIN": min_temp},
                       {"TMAX": max_temp},
                       {"TAVG": avg_temp}]

    temp_stats_data.append(temp_stats_dict)

    return jsonify(temp_stats_data)

#################################################


if __name__ == '__main__':
    app.run(debug=True)