"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""
# from http import HTTPStatus

from flask import Flask, request
from flask_restx import Resource, Api
from flask_cors import CORS
import random
from datetime import datetime
from data import db_connect as dbc
import cities.queries as cq
import countries.queries as ctq

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
CITIES_EP = '/cities'
CITIES_RESP = 'cities'
CITIES_SEARCH_EP = '/cities/search'
COUNTRIES_EP = '/countries'
COUNTRIES_RESP = 'countries'
COUNTRIES_SEARCH_EP = '/countries/search'
STATES_EPS = '/states'




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


@api.route(CITIES_EP)
class Cities(Resource):
    """
    This class handles operations on cities collection.
    """
    def get(self):
        """
        Returns all cities from the database.
        """
        try:
            cities = cq.read()
            return {
                CITIES_RESP: cities,
                'count': len(cities)
            }
        except Exception as e:
            return {'error': str(e)}, 500

    def post(self):
        """
        Create a new city.
        Expected JSON body: {"name": "City Name", "state_code": "ST"}
        """
        try:
            data = request.json
            new_id = cq.create(data)
            return {
                MESSAGE: 'City created successfully',
                'id': str(new_id)
            }, 201
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500


@api.route(f'{CITIES_EP}/<city_name>')
class CityByName(Resource):
    """
    This class handles operations on a specific city.
    """
    def delete(self, city_name):
        """
        Delete a city by name.
        Requires state_code as query parameter.
        """
        try:
            state_code = request.args.get('state_code')
            if not state_code:
                return {'error': 'state_code query parameter is required'}, 400
            cq.delete(city_name, state_code)
            return {MESSAGE: f'City {city_name} deleted successfully'}
        except ValueError as e:
            return {'error': str(e)}, 404
        except Exception as e:
            return {'error': str(e)}, 500


@api.route(CITIES_SEARCH_EP)
class CitiesSearch(Resource):
    """
    Search cities by name and/or state code.
    """
    def get(self):
        """
        Search cities with optional filters.
        Query params: name (substring), state_code (exact)
        """
        try:
            name = request.args.get('name')
            state_code = request.args.get('state_code')
            if not name and not state_code:
                return {
                    'error': 'Provide at least one parameter: '
                             'name or state_code'
                }, 400
            results = cq.search(name=name, state_code=state_code)
            return {
                CITIES_RESP: results,
                'count': len(results)
            }
        except Exception as e:
            return {'error': str(e)}, 500


@api.route(COUNTRIES_EP)
class Countries(Resource):
    """
    This class handles operations on countries collection.
    """
    def get(self):
        """
        Returns all countries from the database.
        Optional query parameter: iso_code (to filter by ISO code)
        """
        try:
            iso_code = request.args.get('iso_code')
            if iso_code:
                country = ctq.find_by_iso_code(iso_code)
                if country:
                    return {COUNTRIES_RESP: country}
                else:
                    error_msg = f'Country with ISO code {iso_code} not found'
                    return {'error': error_msg}, 404

            countries = ctq.read()
            return {
                COUNTRIES_RESP: countries,
                'count': len(countries)
            }
        except Exception as e:
            return {'error': str(e)}, 500

    def post(self):
        """
        Create a new country.
        Expected JSON body: {"name": "Country Name", "iso_code": "CC"}
        """
        try:
            data = request.json
            new_id = ctq.create(data)
            return {
                MESSAGE: 'Country created successfully',
                'id': str(new_id)
            }, 201
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500


@api.route(f'{COUNTRIES_EP}/<country_id>')
class CountryById(Resource):
    """
    This class handles operations on a specific country.
    """
    def get(self, country_id):
        """
        Get a specific country by ID (name).
        """
        try:
            country = ctq.read_one(country_id)
            return {COUNTRIES_RESP: country}
        except ValueError as e:
            return {'error': str(e)}, 404
        except Exception as e:
            return {'error': str(e)}, 500

    def put(self, country_id):
        """
        Update a country by ID.
        Expected JSON body: fields to update
        """
        try:
            data = request.json
            ctq.update(country_id, data)
            return {MESSAGE: f'Country {country_id} updated successfully'}
        except ValueError as e:
            return {'error': str(e)}, 404
        except Exception as e:
            return {'error': str(e)}, 500

    def delete(self, country_id):
        """
        Delete a country by ID.
        """
        try:
            ctq.delete(country_id)
            return {MESSAGE: f'Country {country_id} deleted successfully'}
        except ValueError as e:
            return {'error': str(e)}, 404
        except Exception as e:
            return {'error': str(e)}, 500


@api.route(COUNTRIES_SEARCH_EP)
class CountriesSearch(Resource):
    """
    Search countries by name and/or ISO code.
    """
    def get(self):
        """
        Search countries with optional filters.
        Query params: name (substring), iso_code (exact)
        """
        try:
            name = request.args.get('name')
            iso_code = request.args.get('iso_code')
            if not name and not iso_code:
                err = 'Provide at least one parameter: name or iso_code'
                return {'error': err}, 400
            results = ctq.search(name=name, iso_code=iso_code)
            return {
                COUNTRIES_RESP: results,
                'count': len(results)
            }
        except Exception as e:
            return {'error': str(e)}, 500


if __name__ == '__main__':
    app.run(debug=True)
