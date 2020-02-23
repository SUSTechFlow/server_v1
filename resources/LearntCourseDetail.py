from flask_restful import Resource

from backend.Session import auth_required
from backend.mongo import *
from util import jsonDict, args


class LearntCourseDetail(Resource):
    name = 'learnt_course_detail'

    @auth_required
    @args('username')
    def get(self, username):
        db = db_client[db_name]
        user = db.User.find_one({'username': username})
        learn_course = user['learnt_course']
        course_info = db.Course.aggregate([
            {
                '$match': {'cid': {'$in': learn_course}}
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
                            }
                        },
                        {'$unwind': '$gradePlan'}
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
        return jsonDict(True, '', data=[c for c in course_info])
