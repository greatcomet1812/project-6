"""
Resource: Brevet
"""
from flask import Response, request
from flask_restful import Resource

from database.models import Brevet
# contains brev_dist, begin_date, and checkpoints

class BrevetResource(Resource):
    def get(self, id):
        """ Handles GET requests for a specific Brevet document identified by id """
        brevet = Brevet.objects.get(id=id).to_json()
        return Response(brevet, mimetype="application/json", status=200)

    def put(self, id):
        """ Handles PUT requests to update a specific Brevet document identified by id """
        input_json = request.json
        Brevet.objects.get(id=id).update(**input_json)
        return '', 200

    def delete(self, id):
        """ Handles DELETE requests to delete a specific Brevet document identified by id """
        Brevet.objects.get(id=id).delete()
        return '', 200