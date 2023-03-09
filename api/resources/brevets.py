"""
Resource: Brevets
"""
from flask import Response, request
from flask_restful import Resource

from database.models import Brevet
# contains brev_dist, begin_date, and checkpoints

class BrevetsResource(Resource):
    def get(self):
        """ Handles GET requests for all Brevet documents in the database """
        json_object = Brevet.objects().to_json()
        return Response(json_object, mimetype="application/json", status=200)

    def post(self):
        """ Handles POST requests to create a new Brevet document in the database """
        # Read the entire request body as a JSON
        # This will fail if the request body is NOT a JSON.
        input_json = request.json

        # save the new brevet object and return the ID
        result = Brevet(**input_json).save()
        return {'_id': str(result.id)}, 200

