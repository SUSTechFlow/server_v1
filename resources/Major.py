from flask_restful import Resource

from backend.Session import auth_required
from backend.mongo import *
from util import jsonDict, args


class Major(Resource):
    name = 'major'

    def get(self):
        db = db_client[db_name]
        majors = db.Plan.distinct('major')
        majors = list(filter(lambda c: c is not None and '通识' not in c, majors))
        return jsonDict(True, '', data=majors)
