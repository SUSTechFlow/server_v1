from flask_restful import Resource
import uuid
from backend.EmailSender import EmailSender
from util import args, jsonDict, email_verify
import random
from datetime import datetime, timedelta


def _email_to_sid(e):
    return e.replace('@sustech.edu.cn', '').replace('@mail.sustech.edu.cn', '')


class RegisterLink(Resource):
    """
    EMail verification.
    Send verify code to user's EMail.
    """
    name = 'register_link'
    code = {}

    @args(require=['email'])
    @email_verify
    def get(self, email):
        """
        Send EMail to certain user.
        One user can only be send once per 30 min.
        :param email: GET params or JSON data.
        :return: Result.
        """
        if not _email_to_sid(email).isdigit():
            return jsonDict(False, '老师的邮箱注册暂未开放（防止对老师形成骚扰），请手动联系我们进行注册。')
        if (code_tuple := RegisterLink.code.get(email, None)) is not None:
            if datetime.now() < code_tuple[1] + timedelta(minutes=1):
                return jsonDict(False, '请1分钟后再试。')
        RegisterLink.code[email] = (vcode := str(uuid.uuid4()), datetime.now())
        try:
            email_sender = EmailSender()
            # TODO Remove the following comment mark in production.
            email_sender.send_msg(f'您的SUSTechFlow注册链接是：https://sustechflow.top/register/?vcode={vcode}', email)
            return jsonDict(True, '发送成功')
        except:
            return jsonDict(False, 'Email发送失败')

    @args(require=['email', 'vcode'])
    @email_verify
    def post(self, email, vcode):
        """
        Verify whether a verify code is correct.
        :param email: User's email. JSON data.
        :param vcode: Verify code. JSON data.
        :return:
        """
        if (code_tuple := RegisterLink.code.get(email, None)) is not None:
            if vcode == code_tuple[0] and datetime.now() < code_tuple[1] + timedelta(minutes=30):
                return jsonDict(True, '验证成功')
        return jsonDict(False, '验证码错误')

    @staticmethod
    def verify(email, vcode):
        if (code_tuple := RegisterLink.code.get(email, None)) is not None:
            return code_tuple[0] == str(vcode) and datetime.now() < code_tuple[1] + timedelta(minutes=30)
        return False
