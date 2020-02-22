from flask_restful import Resource
from backend.mongo import *
from util import args, jsonDict


class Rate(Resource):
    name = 'rate'

    @args('cid')
    def get(self, **kwargs):
        """
        Fetch course basic info and their rate.
        :param kwargs: Any filter you want. JSON data.
        :return: Just Try.
        """
        db = db_client[db_name]
        return jsonDict(True, '', data=[c for c in db.Rate.find(kwargs)])
