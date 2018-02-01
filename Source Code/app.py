# Step 4 - Climate App

#### Now that you have completed your initial analysis, design a Flask api based on the queries that you have just developed.
####    - Use FLASK to create your routes.

# Import Dependencies
from flask import Flask,jsonify

import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Setup Database
engine = create_engine("sqlite:///hawaii.sqlite")
# Declare the base as automap_base
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Stations = Base.classes.Stations
Measurements = Base.classes.Measurements

# Create a session for the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

## Routes

@app.route("/")
def welcome():
    return (
    f"Available Routes:<br/>"
    f"<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"<br/>"
    f"/api/v1.0/stations<br/>"
    f"<br/>"
    f"/api/v1.0/tobs<br/>"
    f"<br/>"
    f"/api/v1.0/<start><br/>"
    f"<br/>"
    f"/api/v1.0/<start>/<end>"
            )

### /api/v1.0/precipitation

#### - Query for the dates and temperature observations from the last year.
#### - Convert the query results to a Dictionary using date as the key and tobs as the value.
#### - Return the json representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Query to retrieve the last date in Measurement DB
    last_date = session.query(Measurements.Date).order_by(Measurements.Date.desc()).first()
    last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    # Find the start date of last year
    start_date = last_date - dt.timedelta(days=365)
    # Formatting the start date
    start_date = start_date.strftime("%Y-%m-%d")

    #Query to retreive the precipitation from the begin of last year
    prcp=session.query(Measurements.Date,Measurements.Prcp).\
            filter(Measurements.Date>=start_date).\
            order_by(Measurements.Date.desc()).all()

    # Create a list to store the result for each date as a dictionary in the list
    prcp_list=[]
    for item in prcp:
        prcp_item={"Date": item[0], "Precipitation": item[1]}
        prcp_list.append(prcp_item)
        
    # Return the jsonify list
    return jsonify(prcp_list)

### /api/v1.0/stations

#### - Return a json list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations_list():
    print("Processing the Station List Query")
    # Query to retrieve the station and station name
    station_results = session.query(Stations.Name,Stations.Station).all()

    # Create a list to store the result in dictionary format
    station_list = []
    for station in station_results:
        stat={"Name":station[0], "Station": station[1]}
        station_list.append(stat)

    # Return the jsonify list
    return jsonify(station_list)

### /api/v1.0/tobs

#### Return a json list of Temperature Observations (tobs) for the previous year

@app.route("/api/v1.0/tobs")
def temp_prev_year():
    print("Processing the Temperature Observation for the previous year")
    
    # Retrieve the start and end dates
    # Query to retrieve the last date in Measurement DB
    last_date = session.query(Measurements.Date).order_by(Measurements.Date.desc()).first()
    # Converting end date into datetime format
    end_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')

    # Calculating the first date based on the end date
    first_date="%d-%d-%d"%(end_date.year-1,end_date.month,end_date.day)
    # Converting the start date into datetime format
    start_date=dt.datetime.strptime(first_date, '%Y-%m-%d').strftime("%Y-%m-%d")
    # Converting the end date into neccessary datetime format
    end_date=end_date.strftime("%Y-%m-%d")

    # Use the start date and end date calculated for query for the previous year data.
    temp_prev_year=session.query(Measurements.Date,Measurements.Tobs).\
                    filter(Measurements.Date>=start_date, Measurements.Date<=end_date).\
                    order_by(Measurements.Date.desc()).all()

    # Create a list to store the result in dictionary format
    temp_list = []
    for row in temp_prev_year:
        temp = {"Date":row[0], "Temp": row[1]}
        temp_list.append(temp)

    # Return the jsonify list
        return jsonify(temp_list)

### /api/v1.0/start and /api/v1.0/start/end

#### -Return a json list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

#### -When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

#### -When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>")
def temp_analysis_start(start):
    print("Processing the Temperature Analaysis from the start date")
    # Query to get the tmin, tavg and tmax starting from the start date
    temp_analysis_results = session.query(func.min(Measurements.Tobs),func.avg(Measurements.Tobs),func.max(Measurements.Tobs)).\
                            filter(Measurements.Date>=start).order_by(Measurements.Date.desc()).all()
        
    # Converting the tuple to a list
    temp_analysis_results = list(np.ravel(temp_analysis_results))
    
    # Storing the result in a dictionary list
    temp_result1=[{"Start Date": start , "TMIN":temp_analysis_results[0],\
                  "TAVG" : round(temp_analysis_results[1],2) , "TMAX" : temp_analysis_results[2]}]
    
    # Return the jsonify list
    return jsonify(temp_result1)

@app.route("/api/v1.0/<start>/<end>")
def temp_analysis_start_end(start,end):
    print("Processing the Temperature Analaysis from the start date to the end date.")
    # Query to get the tmin, tavg and tmax starting from the start date
    temp_analysis_results = session.query(func.min(Measurements.Tobs),func.avg(Measurements.Tobs),func.max(Measurements.Tobs)).\
                            filter(Measurements.Date>=start,Measurements.Date<=end).\
                            order_by(Measurements.Date.desc()).all()
        
    # Converting the tuple to a list
    temp_analysis_results = list(np.ravel(temp_analysis_results))
    
    # Storing the result in a dictionary list
    temp_result2=[{"Start Date": start , "End Date" : end , "TMIN":temp_analysis_results[0],\
                  "TAVG" : temp_analysis_results[1] , "TMAX" : temp_analysis_results[2]}]
    
    # Return the jsonify list
    return jsonify(temp_result2)

#####################################################################################################################################

if __name__ == '__main__':
    app.run(debug=True)

#####################################################################################################################################