8
# Import the dependencies.
import datetime as dt
import sqlalchemy
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///../Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

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
        f"/api/v1.0/ **enter date in YYYYMMDD format** <br/>"
        f"/api/v1.0/</ **enter start date in YYYYMMDD format/end date in YYYYMMDD**start/end>"
    )

# Last 2 "f" need a date inputted formatted to YYYYMMDD
#################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year from the last date in data set.
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #  query and retrieve the data and precipitation scores
    data_prcp = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= one_year_ago).all()
    session.close()
    precip = []
    for date, prcp in data_prcp:
        precip_dict = {}
        precip_dict["Date"] = date
        precip_dict["Precipitation"] = prcp
        precip.append(precip_dict)
    return jsonify(precip)

#################################################
@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(station.station).all()
    session.close()
    all_names = list(np.ravel(stations))
    return jsonify(all_names)
#################################################
@app.route("/api/v1.0/tobs")
def tobs():

    # Calculate the date one year from the last date in data set.
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Query the last 12 months of temperature observation data for station USC00519281
    data_temp = session.query(measurement.station, measurement.date, measurement.tobs).\
        filter(measurement.date >= one_year_ago).\
        filter(measurement.station == 'USC00519281').all()
    session.close()
    temp = []
    for station, date, tobs in data_temp:
        temp_dict = {}
        temp_dict["Station"] = station
        temp_dict["Date"] = date
        temp_dict["Temperature"] = tobs
        temp.append(temp_dict)
    return jsonify(temp)

#################################################
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_date(start=None, end=None):

    # create a Select statement
    sel = [func.min(measurement.tobs), func.avg(
        measurement.tobs), func.max(measurement.tobs)]
    if not end:
        start = dt.datetime.strptime(start, "%Y%m%d")
        results = session.query(*sel).\
            filter(measurement.date >= start).all()
        session.close()
        temps = list(np.ravel(results))
        return jsonify(temps)

    # calculate the minimum. maxmimum, and max temperatures
    start = dt.datetime.strptime(start, "%Y%m%d")
    end = dt.datetime.strptime(end, "%Y%m%d")
    results = session.query(*sel).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()
    session.close()

    # Put results into an array and order them
    temps = list(np.ravel(results))
    return jsonify(temps=temps)
if __name__ == "__main__":
    app.run(debug=True)