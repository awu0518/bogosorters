"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""
# from http import HTTPStatus

from flask import Flask  # , request
from flask_restx import Resource, Api  # , fields  # Namespace
from flask_cors import CORS
import random
from datetime import datetime
from data import db_connect as dbc

# import werkzeug.exceptions as wz

app = Flask(__name__)
CORS(app)
api = Api(app)

ENDPOINT_EP = '/endpoints'
ENDPOINT_RESP = 'Available endpoints'
HELLO_EP = '/hello'
HELLO_RESP = 'hello'
MESSAGE = 'Message'
TIMESTAMP_EP = '/timestamp'
TIMESTAMP_RESP = 'timestamp'
RANDOM_EP = '/random'
RANDOM_RESP = 'random_number'
DICE_EP = '/dice'
DICE_RESP = 'rolls'
HEALTH_EP = '/health'
HEALTH_RESP = 'status'


@api.route(HELLO_EP)
class HelloWorld(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    def get(self):
        """
        A trivial endpoint to see if the server is running.
        """
        return {HELLO_RESP: 'world'}


@api.route(ENDPOINT_EP)
class Endpoints(Resource):
    """
    This class will serve as live, fetchable documentation of what endpoints
    are available in the system.
    """
    def get(self):
        """
        The `get()` method will return a sorted list of available endpoints.
        """
        endpoints = sorted(rule.rule for rule in api.app.url_map.iter_rules())
        return {ENDPOINT_RESP: endpoints}


@api.route(TIMESTAMP_EP)
class Timestamp(Resource):
    """
    This class returns the current server timestamp.
    """
    def get(self):
        """
        Returns the current server time in ISO format.
        """
        current_time = datetime.now().isoformat()
        return {
            TIMESTAMP_RESP: current_time,
            'unix': datetime.now().timestamp()
        }


@api.route(RANDOM_EP)
class RandomNumber(Resource):
    """
    This class generates and returns random numbers.
    """
    def get(self):
        """
        Returns a random integer between 1 and 100.
        """
        return {
            RANDOM_RESP: random.randint(1, 100),
            'min': 1,
            'max': 100
        }


@api.route(DICE_EP)
class DiceRoller(Resource):
    """
    This class simulates rolling dice.
    """
    def get(self):
        """
        Simulates rolling 2 six-sided dice and returns the results.
        """
        num_dice = 2
        sides = 6
        rolls = [random.randint(1, sides) for _ in range(num_dice)]
        return {
            DICE_RESP: rolls,
            'total': sum(rolls),
            'num_dice': num_dice,
            'sides': sides
        }


@api.route(HEALTH_EP)
class Health(Resource):
    """
    Basic health check endpoint.
    """
    def get(self):
        """
        Returns server liveness and database health details.
        """
        now = datetime.now()
        db_status = dbc.ping()
        overall = 'ok' if db_status.get('ok') else 'degraded'
        return {
            HEALTH_RESP: overall,
            'timestamp': now.isoformat(),
            'unix': now.timestamp(),
            'db': db_status
        }


if __name__ == '__main__':
    app.run(debug=True)
