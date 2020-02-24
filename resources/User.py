from resources.Key import Key
from backend.Session import session, auth_required
from flask_restful import Resource
from backend.mongo import db_client, db_name
from resources.Verification import Verification
from util import jsonDict, args, email_verify


class User(Resource):
    """
    User registration and login.
    """
    name = 'user'

    @auth_required
    def get(self, username):
        """
        Respond the username based on request Authentication.
        :param username: Provided by *auth_required*, see its document.
        :return: username.
        """
        return jsonDict(True, msg='成功', username=username)

    @args(require=['username', 'password'])
    def post(self, username, password):
        """
        User login.
        :param username: Username, JSON data.
        :param password: Password, JSON data.
        :return: Token and username. The token should be attached when request a *auth_required* API.
        """
        db = db_client[db_name]
        if (res := db.User.find_one({'username': username})) is None:
            res = db.User.find_one({'email': username})
        if res is None:
            return jsonDict(False, '用户不存在')
        username = res['username']
        permanent_token = res['permanent_token']
        valid = Key.checkpw(password, permanent_token)
        if not valid:
            return jsonDict(False, '用户名或密码错误')
        else:
            new_temp_token = session.sign_jwt_token(username)
            db.User.find_one_and_update({'username': username}, {'$set': {'temp_token': new_temp_token}})
            return jsonDict(True, '登录成功', temp_token=new_temp_token, username=username)

    @args(require=['username', 'password', 'new_password'])
    def patch(self, username, password, new_password):
        """
        Change user's password. NOT USED AND TESTED YET.
        :param username:
        :param password:
        :param new_password:
        :return:
        """
        db = db_client[db_name]
        if (res := db.User.find_one({'username': username})) is None:
            res = db.User.find_one({'email': username})
        if res is None:
            return jsonDict(False, '用户不存在')
        username = res['username']
        if res is None:
            return jsonDict(False, '用户不存在')
        permanent_token = res['permanent_token']
        valid = Key.checkpw(password, permanent_token)
        if not valid:
            return jsonDict(False, '用户名或密码错误')
        else:
            new_permanent_token = Key.hashpw(new_password)
            db.User.find_one_and_update({'username': username}, {'$set': {'permanent_token': new_permanent_token}})
            return jsonDict(True, '修改成功')

    @args(require=['username', 'password', 'email', 'vcode'])
    @email_verify
    def put(self, username, password, email, vcode):
        """
        User registration.
        :param username: JSON data.
        :param password: JSON data.
        :param email: JSON data.
        :param vcode: Verify code JSON data.
        :return: Token and username. The token should be attached when request a *auth_required* API.
        """
        if not Verification.verify(email, vcode):
            return jsonDict(False, '验证码错误')
        permanent_token = Key.hashpw(password)
        temp_token = session.sign_jwt_token(username)
        db = db_client[db_name]
        if db.User.count_documents({"username": username}) >= 1:
            return jsonDict(False, '用户已存在')
        if db.User.count_documents({"email": email}) >= 1:
            return jsonDict(False, '用户已存在')
        ins_res = db.User.insert_one({
            "username": username,
            "email": email,
            "permanent_token": permanent_token,
            'learnt_course': []
        })
        if not ins_res.acknowledged:
            return jsonDict(False, '无法与数据库通信')
        return jsonDict(True, '注册成功', temp_token=temp_token, username=username)
