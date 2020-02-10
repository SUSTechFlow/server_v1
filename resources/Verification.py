from flask_restful import Resource

from backend.EmailSender import EmailSender
from util import args, jsonDict, email_verify
import random
from datetime import datetime, timedelta


class Verification(Resource):
    name = 'verify'
    code = {}

    @args(require=['email'])
    @email_verify
    def get(self, email):
        if (code_tuple := Verification.code.get(email, None)) is not None:
            if datetime.now() < code_tuple[1] + timedelta(minutes=30):
                return jsonDict(False, '请30分钟后再试。')
        Verification.code[email] = (vcode := str(int(random.uniform(100000, 999999))), datetime.now())
        try:
            email_sender = EmailSender()
            # TODO Remove the following comment mark in production.
            email_sender.send_msg(f'你的SUSTechFlow验证码是：{vcode}', email)
            return jsonDict(True, '发送成功')
        except:
            return jsonDict(False, 'Email发送失败，每天仅限200人。')

    @args(require=['email', 'vcode'])
    @email_verify
    def post(self, email, vcode):
        if (code_tuple := Verification.code.get(email, None)) is not None:
            if vcode == code_tuple[0] and datetime.now() < code_tuple[1] + timedelta(minutes=30):
                return jsonDict(True, '验证成功')
        return jsonDict(False, '验证码错误')

    @staticmethod
    def verify(email, vcode):
        if (code_tuple := Verification.code.get(email, None)) is not None:
            return code_tuple[0] == str(vcode)
        return False