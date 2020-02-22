import csv
import re

from flask_restful import reqparse

from backend.mongo import db_client, db_name


def jsonDict(success, msg, **kwargs):
    r = kwargs
    r['success'] = success
    r['msg'] = msg
    return r


def dict_filter(d):
    if isinstance(d, dict):
        return {k: dict_filter(v) for k, v in d.items() if v is not None and k != '_id'}
    elif isinstance(d, list):
        return [dict_filter(x) for x in d]
    else:
        return d


def email_verify(func):
    def decorated_fun(self, *args, **kwargs):
        pattern = '''[\w!#$%&'*+/=?^_`{|}~-]+(?:\.[\w!#$%&'*+/=?^_`{|}~-]+)*@(mail\.sustech\.edu\.cn)|(mail\.sustc\.edu\.cn)|(sustech\.edu\.cn)|(sustc\.edu\.cn)'''
        if re.match(pattern, kwargs['email']) is None:
            return jsonDict('False', '邮箱格式错误')
        return func(self, *args, **kwargs)

    return decorated_fun


def args(*args_list, require=None):
    if require is None:
        require = []

    def args_decorator(func):
        def decorated_func(self, *args, **kwargs):
            self.parser = reqparse.RequestParser()
            new_require = []
            for arg in list(args_list) + require:
                if isinstance(arg, tuple):
                    if arg[1] is list:
                        self.parser.add_argument(arg[0], action='append')
                    else:
                        self.parser.add_argument(arg[0], type=arg[1])
                    if arg in require:
                        new_require.append(arg[0])
                else:
                    self.parser.add_argument(arg)
            for k, v in self.parser.parse_args().items():
                if kwargs.get(k) is not None:
                    continue
                kwargs[k] = v
                if k in new_require + require and v is None:
                    return jsonDict(False, f'缺少必须参数{k}，请不要伪造请求。')
            kwargs = dict_filter(kwargs)
            try:
                return dict_filter(func(self, *args, **kwargs))
            except Exception as e:
                return jsonDict(False, e.__str__())

        return decorated_func

    return args_decorator



