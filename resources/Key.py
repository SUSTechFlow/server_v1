import base64

import bcrypt
import rsa
from flask_restful import Resource


class Key(Resource):
    secret = 'dfjwoeqiur90824ur89jfojda9f2u4098urjwieojf92048ur902j9ew8urj924fuhjrw98qur2980urjieowjf9024'
    name = 'key'
    pubkey, privkey = rsa.newkeys(1024)

    @staticmethod
    def encode(s):
        return base64.encodebytes(rsa.encrypt(s.encode(), Key.pubkey)).decode()

    @staticmethod
    def decode(s):
        return rsa.decrypt(base64.decodebytes(s.encode()), Key.privkey).decode()

    @staticmethod
    def hashpw(s):
        salt = bcrypt.gensalt()
        h = base64.encodebytes(bcrypt.hashpw(s.encode(), salt)).decode()
        return h

    @staticmethod
    def checkpw(p, s):
        return bcrypt.checkpw(p.encode(), base64.decodebytes(s.encode()))

    def get(self):
        return Key.pubkey.save_pkcs1().decode().replace('\n', '')

    def put(self):
        Key.pubkey, Key.privkey = rsa.newkeys(1024)
        return Key.pubkey.save_pkcs1().decode().replace('\n', '')

