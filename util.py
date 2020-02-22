import re

from flask_restful import reqparse


def jsonDict(success, msg, **kwargs):
    """
    A helper function to regularize the response of ReSTful API
    :param success: A boolean value to indicate the result.
    :param msg: Error/Success message to send.
    :param kwargs: Other necessary fields, like data/username...
    :return: Structured JSON dict.
    """
    r = kwargs
    r['success'] = success
    r['msg'] = msg
    return r


def dict_filter(d):
    """
    A helper function that filter the **_id** field from MongoDB doc recursively.
    :param d: The MongoDB doc need to be filtered.
    :return: A MongoDB doc with no **_id** field
    """
    if isinstance(d, dict):
        return {k: dict_filter(v) for k, v in d.items() if v is not None and k != '_id'}
    elif isinstance(d, list):
        return [dict_filter(x) for x in d]
    else:
        return d


def email_verify(func):
    """
    A decorator function to verify whether EMail belongs to SUSTC.
    :param func: A function with EMail parameter.
    :return: Result of func
    """
    def decorated_fun(self, *args, **kwargs):
        pattern = '''[\w!#$%&'*+/=?^_`{|}~-]+(?:\.[\w!#$%&'*+/=?^_`{|}~-]+)*@(mail\.sustech\.edu\.cn)|(mail\.sustc\.edu\.cn)|(sustech\.edu\.cn)|(sustc\.edu\.cn)'''
        if re.match(pattern, kwargs['email']) is None:
            return jsonDict('False', '邮箱格式错误')
        return func(self, *args, **kwargs)

    return decorated_fun


def args(*args_list, require=None):
    """
    Parser decorator, transform the JSON request into the arguments that API can understand, like list, bool, etc.
    :param args_list: [Tuple(arg, type) | arg] A list contains optional arguments.
    :param require: [Tuple(arg, type) | arg] A list contains necessary arguments.
    :return: Result of func
    """
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



