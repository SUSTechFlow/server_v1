from flask_restful import Resource
from backend.mongo import db_client, db_name
from util import args, jsonDict


class PluginPlan(Resource):
    name = 'plugin_plan'

    @args(require=[('cids', list)])
    def post(self, cids):
        db = db_client[db_name]
        course_info = db.Course.aggregate([
            {
                '$match': {'cid': {'$in': cids}}
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
