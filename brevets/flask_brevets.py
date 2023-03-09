"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import os
import flask
from flask import redirect, url_for, request
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import requests
import logging

###
# Globals
###
app = flask.Flask(__name__)
app.debug = True if "DEBUG" not in os.environ else os.environ["DEBUG"]
port_num = True if "PORT" not in os.environ else os.environ["PORT"]
app.logger.setLevel(logging.DEBUG)

###
# API Callers
###
API_ADDR = os.environ["API_ADDR"]
API_PORT = os.environ["API_PORT"]
API_URL = f"http://{API_ADDR}:{API_PORT}/api/"

def insert(brev_dist, begin_date, checkpoints):
    """
    Inserts a new checkpoint list into the database by calling the API.
    Args:
        brevet distance: string
        begin_date: string
        checkpoints: list of dictionaries
    """
    _id = requests.post(f"{API_URL}/brevets", json={"brev_dist": brev_dist, "begin_date": begin_date, "checkpoints": checkpoints}).json()
    return _id

def fetch():
    """
    Obtains the newest document in the "lists" collection in database
    by calling the RESTful API.

    Returns:
        A tuple containing brevet distance(string), begin_date(string), checkpoints(list of dictionaries)
    """
    # Get documents (rows) in our collection (table),
    # Sort by primary key in descending order and limit to 1 document (row)
    # This translates into finding the newest inserted document.
    brevets = requests.get(f"{API_URL}/brevets").json()
    brevet = brevets[-1]
    return brevet["brev_dist"], brevet["begin_date"], brevet["checkpoints"]

###
# Pages
###
@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")
    km = request.args.get('km', 999, type=float)
    app.logger.debug("km={}".format(km))
    app.logger.debug("request.args: {}".format(request.args))

    # get brevet distance and start time from the template
    brev_dist = request.args.get('brev_dist', type=int)
    start_time = request.args.get('start_time', type=str)
    app.logger.debug("request.args: {}".format(request.args))

    open_time = acp_times.open_time(km, brev_dist, arrow.get(start_time, 'YYYY-MM-DDTHH:mm')).format('YYYY-MM-DDTHH:mm')
    close_time = acp_times.close_time(km, brev_dist, arrow.get(start_time, 'YYYY-MM-DDTHH:mm')).format('YYYY-MM-DDTHH:mm')
    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)


@app.route("/insert_brevet", methods=["POST"])
def insert_brevet():
    try:
        input_json = request.json
        brev_dist = input_json["brev_dist"] 
        begin_date = input_json["begin_date"] 
        checkpoints = input_json["checkpoints"] 

        # Insert brevet data into database
        brev_id = insert(brev_dist, begin_date, checkpoints)

        return flask.jsonify(result={},
                        message="Inserted!", 
                        status=1,
                        mongo_id=brev_id)
    except:
        return flask.jsonify(result={},
                        message="Server error", 
                        status=0, 
                        mongo_id='None')


@app.route("/fetch_brevet")
def fetch_brevet():
    try:
        # Fetch the newest brevet data from the database
        brev_dist, begin_date, checkpoints = fetch()    

        return flask.jsonify(
                result={"brev_dist": brev_dist, "begin_date": begin_date, "checkpoints": checkpoints}, 
                status=1,
                message="Successfully fetched brevet data")
    except:
        return flask.jsonify(
                result={}, 
                status=0,
                message="Cannot be fetched")


#############

if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(os.environ["PORT"]))
    app.run(port=os.environ["PORT"], host="0.0.0.0")
