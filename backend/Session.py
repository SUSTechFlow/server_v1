from datetime import datetime, timedelta

import jwt
from flask_restful import reqparse
from jwt import DecodeError

from resources.Key import Key
from util import jsonDict


class Session:
    def __init__(self):
        self.ss = {}

    def sign_jwt_token(self, username):
        expire_time = str(datetime.now() + timedelta(hours=24))
        token = jwt.encode({'username': username, 'expire_time': expire_time},
                           Key.secret).decode()
        self.ss[token] = {'username': username, 'expire_time': expire_time}
        return token

    def check_jwt_token(self, token):
        session_info = self.ss.get(token, None)
        if session_info is not None:
            if datetime.now() < datetime.fromisoformat(session_info['expire_time']):
                return True, session_info['username']
            else:
                del self.ss[token]
                return False, session_info['username']
        try:
            d = jwt.decode(token, Key.secret)
            if datetime.now() < datetime.fromisoformat(d['expire_time']):
                return True, d['username']
            else:
                return False, d['username']
        except DecodeError:
            return False, None


session = Session()


def auth_required(func):
    def auth_required_func(self, *args, **kwargs):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('Authorization', location='headers')
        temp_token = self.parser.parse_args()['Authorization']
        if temp_token is None:
            return jsonDict(False, '认证失败')
        success, username = session.check_jwt_token(temp_token)
        if success:
            kwargs['username'] = username
            return func(self, *args, **kwargs)
        else:
            return jsonDict(False, '认证失败')
    return auth_required_func
