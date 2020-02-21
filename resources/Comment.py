from flask_restful import Resource
from datetime import datetime
from backend.Session import auth_required
from backend.mongo import *
from util import args, jsonDict


def rate_verify(rate):
    required_field = ['likes', 'useful', 'easy']
    if isinstance(rate, dict):
        for field in required_field:
            if rate.get(field) is None:
                return jsonDict(False, '评分数据不完整。')
        rate['ratings'] = 5
        return jsonDict(True, '', rate=rate)
    else:
        return jsonDict(False, 'rate必须是字典类型。')


class Comment(Resource):
    name = 'comment'

    @auth_required
    @args('gpa', require=['cid', 'content', 'commentBy', 'term', ('willing',bool), ('anonymous', bool), ('rate', dict), ('taught', list)])
    def put(self, **kwargs):
        rate_tuple = rate_verify(kwargs['rate'])
        if rate_tuple['success']:
            kwargs['rate'] = rate_tuple['rate']
            kwargs['helpful'] = 0
            kwargs['year'] = datetime.now().year
            kwargs['month'] = datetime.now().month
            kwargs['day'] = datetime.now().day
            db = db_client[db_name]
            db.Comment.find_one_and_replace({'cid': kwargs['cid'], 'commentBy': kwargs['commentBy']}, kwargs, upsert=True)
            return jsonDict(True, '评论成功！')
        else:
            return rate_tuple

    @auth_required
    @args(require=['commentBy', 'cid'])
    def get(self, **kwargs):
        db = db_client[db_name]
        return jsonDict(True, '', data=db.Comment.find_one(kwargs))
