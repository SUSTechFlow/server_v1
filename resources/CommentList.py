from flask_restful import Resource
from backend.mongo import *
from util import args, jsonDict


class CommentList(Resource):
    name = 'comment_list'

    @args(require=['cid'])
    def get(self, **kwargs):
        db = db_client[db_name]
        comments = list(db.Comment.find(kwargs))
        for c in comments:
            if c['anonymous']:
                c['commentBy'] = '佚名'
        comments = list(filter(lambda a: a['content'] != '', comments))
        return jsonDict(True, '', data=comments)
