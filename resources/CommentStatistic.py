from flask_restful import Resource
from backend.mongo import *
from util import args, jsonDict


class CommentStatistic(Resource):
    name = 'comment_statistic'

    @args(require=['cid'])
    def get(self, **kwargs):
        db = db_client[db_name]
        comments = list(db.Comment.find(kwargs))
        data = {
            'likes': [0 for _ in range(11)],
            'useful': [0 for _ in range(11)],
            'easy': [0 for _ in range(11)]
        }
        for c in comments:
            for k, v in c['rate'].items():
                if k == 'ratings':
                    continue
                data[k][int(v*2)] += 1
        return jsonDict(True, '', data=data)
