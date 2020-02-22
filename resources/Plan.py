from flask_restful import Resource
from backend.mongo import *
from util import args, jsonDict


class Plan(Resource):
    name = 'plan'

    @args(require=['cid'])
    def get(self, **kwargs):
        """
        Fetch plan info.
        :param kwargs: Any filter you want.
        :return: Just Try.
        """
        db = db_client[db_name]
        return jsonDict(True, '', data=[c for c in db.Plan.find(kwargs)])
