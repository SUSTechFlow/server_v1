from flask_restful import Resource
from backend.mongo import *
from util import args, jsonDict


class Course(Resource):
    name = 'course'

    @args(require=['cid'])
    def get(self, **kwargs):
        db = db_client[db_name]
        course_info = db.Course.aggregate([
            {
                '$match': kwargs
            },
            {
                '$lookup': {
                    'from': 'Detail',
                    'localField': 'cid',
                    'foreignField': 'cid',
                    'as': 'detail'
                }
            },
            {
                '$lookup': {
                    'from': 'Comment',
                    'let': {'course_cid': '$cid'},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$cid', '$$course_cid']}}},
                        {'$replaceRoot': {'newRoot': '$rate'}},
                    ],
                    'as': "rate"
                }
            },
            {'$project': {
                'rate': {'$concatArrays': [[{'ratings': 0, 'likes': 0, 'useful': 0, 'easy': 0}], '$rate']},
                'cid': '$cid',
                'name': '$name',
                'faculty': '$faculty',
                'detail': '$detail',
                'taughtBy': '$taughtBy'
            }},
            {
                '$lookup': {
                    'from': 'Plan',
                    'let': {'course_cid': '$cid'},
                    'pipeline': [
                        {'$match': {'$expr': {'$eq': ['$cid', '$$course_cid']}}},
                        {'$group':
                            {
                                '_id': '$grade',
                                'grade': {'$first': '$grade'},
                                'gradePlan': {'$addToSet':
                                    {
                                        'optionalType': '$optionalType',
                                        'faculty': '$faculty',
                                        'major': '$major',
                                        'category': '$category',
                                    }
                                },
                            }}
                    ],
                    'as': 'plan'
                }
            },
            {'$unwind': '$detail'},
            {
                '$group': {
                    '_id': '$cid',
                    'cid': {'$first': '$cid'},
                    'name': {'$first': '$name'},
                    'taughtBy': {'$addToSet': '$taughtBy'},
                    'detail': {'$first': '$detail'},
                    'ratings': {'$first': {'$sum': '$rate.ratings'}},
                    'likes': {'$first': {'$sum': '$rate.likes'}},
                    'useful': {'$first': {'$sum': '$rate.useful'}},
                    'easy': {'$first': {'$sum': '$rate.easy'}},
                    'plan': {'$first': '$plan'}
                }
            },
        ])
        return jsonDict(True, '', data=[c for c in course_info][0])
