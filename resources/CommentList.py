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
                c['username'] = '身体好轻，这样的体验从未有过，已经没有什么好害怕的了，因为！我不再是一个人了！'
            if not c['willing']:
                c['gpa'] = '奇迹和魔法都是存在的。'
        comments = list(filter(lambda a: a['content'] != '', comments))
        return jsonDict(True, '', data=comments)
