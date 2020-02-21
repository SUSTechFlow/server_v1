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
                    'ratings': {'$first': {'$sum': '$rate.ratings'}},
                    'likes': {'$first': {'$sum': '$rate.likes'}},
                    'useful': {'$first': {'$sum': '$rate.useful'}},
                    'easy': {'$first': {'$sum': '$rate.easy'}}
                }},

            ]})
