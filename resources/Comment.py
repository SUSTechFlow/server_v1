from flask_restful import Resource

from backend.Session import auth_required
from backend.mongo import *
from util import args, jsonDict


def rate_verify(rate):
    required_field = ['likes', 'useful', 'easy']
    if isinstance(rate, dict):
        for field in required_field:
            if rate.get(field, None) is None:
                return jsonDict(False, '评分数据不完整。')
        rate['ratings'] = 1
        return jsonDict(True, '', rate=rate)
    else:
        return jsonDict(False, 'rate必须是字典类型。')


class Comment(Resource):
    name = 'comment'

    @auth_required
    @args(require=['cid', 'content', 'commentBy', ('anonymous', bool), ('rate', dict), ('taughtBy', list)])
    def put(self, **kwargs):
        rate_tuple = rate_verify(kwargs['rate'])
        if rate_tuple['success']:
            kwargs['rate'] = rate_tuple['rate']
            db = db_client[db_name]
            db.Comment.find_one_and_replace({'cid': kwargs['cid'], 'commentBy': kwargs['commentBy']}, kwargs, upsert=True)
            return jsonDict(True, '评论成功！')
        else:
            return rate_tuple

    @auth_required
    @args(require=['cid', 'commentBy'])
    def get(self, **kwargs):
        db = db_client[db_name]
        return jsonDict(True, '', data=db.Comment.find_one(kwargs))
