import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurements = Base.classes.measurements
Stations = Base.classes.stations

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
        f"/api/v1.0/precipitation -- Returns total precipitation readings per day for previous year<br/>"
        f"/api/v1.0/stations -------- Returns all information on stations<br/>"
        f"/api/v1.0/tobs ------------ Returns average TOBS readings per day for previous year<br/>"
        f"/api/v1.0/:start: ---------- Takes start and end date in YYYY-MM-DD format;<br/>"
        f"/api/v1.0/:start:/:end: --- Returns the minimum, maximum, and average temperature for the range provided (max date 2017-08-23)"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """
    Returns total precipitation readings for previous year
    """
    # Query the date and precipitation levels
    precipitation = session.query(Measurements.date,Measurements.prcp)
    
    # Create Dataframe and group by Date
    precip_df = pd.read_sql(precipitation.statement, precipitation.session.bind)
    by_date = precip_df.groupby(["date"]).sum()
    
    # Grab tail 365 entries for look at most recent year
    last_year = by_date.tail(365)
    
    # Convert to dictionary
    last_year_dict = last_year.to_dict(orient="index")

    return jsonify(last_year_dict)


@app.route("/api/v1.0/stations")
def stations():
    """
    Returns all information on stations
    """
    # Query station information
    station_query = session.query(Stations)
    
    # Convert to DataFrame, then to Dictionary
    station_df = pd.read_sql(station_query.statement, station_query.session.bind)
    station_dict = station_df.to_dict(orient="index")

    return jsonify(station_dict)


@app.route("/api/v1.0/tobs")
def tobs():
    """
    Returns average TOBS readings per day for previous year
    """
    # Query tobs information
    tobs = session.query(Measurements.date,Measurements.tobs)
    
    # Convert to Dataframe
    tobs_df = pd.read_sql(tobs.statement,tobs.session.bind)
    
    # Sort by date, pull last year of data only
    last_year = tobs_df.groupby(tobs_df["date"]).mean()
    last_year = last_year.tail(365)
    
    # Convert to dictionary
    last_year_dict = last_year.to_dict(orient="index")

    return jsonify(last_year_dict)


@app.route("/api/v1.0/<start>")
def start(start):
    """
    Return the minimum, maximum, and average temperature for the range provided (max date 2017-08-23)
    """
    # Start the query and create a dataframe
    query = session.query(Measurements.date, Measurements.tobs)
    dataframe = pd.read_sql(query.statement, query.session.bind)

    # Trim dataframe to selected dates
    trimmed = dataframe.loc[dataframe["date"] >= start]

    # Group by Date
    avg_temp = trimmed.groupby("date").mean()
    
    # Set Min and Max temp variables / Calculate Y-Error
    min_temp = avg_temp["tobs"].min()
    max_temp = avg_temp["tobs"].max()

    # Calculate Average Temp and create Dictionary
    avg_temp = avg_temp["tobs"].mean()
    forecast = {"average_temp":avg_temp,
                "minimum_temp":min_temp,
                "maximum_temp":max_temp}
    
    return jsonify(forecast)

@app.route("/api/v1.0/<start>/<stop>")
def stop(start,stop):
    """
    Return the minimum, maximum, and average temperature for the range provided (max date 2017-08-23)
    """
    # Start the query and create a dataframe
    query = session.query(Measurements.date, Measurements.tobs)
    dataframe = pd.read_sql(query.statement, query.session.bind)

    # Trim dataframe to selected dates
    trimmed = dataframe.loc[dataframe["date"] >= start]
    trimmed = dataframe.loc[dataframe["date"] <= stop]

    # Group by Date
    avg_temp = trimmed.groupby("date").mean()
    
    # Set Min and Max temp variables / Calculate Y-Error
    min_temp = avg_temp["tobs"].min()
    max_temp = avg_temp["tobs"].max()

    # Calculate Average Temp and create Dictionary
    avg_temp = avg_temp["tobs"].mean()
    forecast = {"average_temp":avg_temp,
                "minimum_temp":min_temp,
                "maximum_temp":max_temp}
    
    return jsonify(forecast)


if __name__ == '__main__':
    app.run(debug=True)
