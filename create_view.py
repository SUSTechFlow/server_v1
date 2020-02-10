from backend.mongo import *

db = db_client[db_name]
db.command({"create": "Rate",
            "viewOn": "Course",
            "pipeline": [
                {'$group': {'_id': '$cid',
                            'cid': {'$first': '$cid'},
                            'name': {'$first': '$name'},
                            'faculty': {'$first': '$faculty'}}},
                {'$lookup':
                    {
                        'from': 'Comment',
                        'let': {'course_cid': '$cid'},
                        'pipeline': [
                            {'$match': {'$expr': {'$eq': ['$cid', '$$course_cid']}}},
                            {'$replaceRoot': {'newRoot': '$rate'}},
                        ],
                        'as': 'rate'
                    }
                },
                {'$project': {
                    'rate': {'$concatArrays': [[{'ratings': 0, 'likes': 0, 'useful': 0, 'easy': 0}], '$rate']},
                    'cid': '$cid',
                    'name': '$name',
                    'faculty': '$faculty'
                }},
                {'$group': {
                    '_id': '$cid',
                    'cid': {'$first': '$cid'},
                    'name': {'$first': '$name'},
                    'faculty': {'$first': '$faculty'},
                    'ratings': {'$sum': {'$sum': '$rate.ratings'}},
                    'likes': {'$sum': {'$sum': '$rate.likes'}},
                    'useful': {'$sum': {'$sum': '$rate.useful'}},
                    'easy': {'$sum': {'$sum': '$rate.easy'}}
                }},

            ]})
