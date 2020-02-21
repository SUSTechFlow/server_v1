from flask_restful import Resource
from backend.Session import auth_required
from backend.mongo import *
from util import args, jsonDict


class Plan(Resource):
    name = 'plan'

    @args(require=['cid'])
    def get(self, **kwargs):
        db = db_client[db_name]
        return jsonDict(True, '', data=[c for c in db.Plan.find(kwargs)])
