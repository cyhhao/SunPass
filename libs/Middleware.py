# coding:utf8
import json
import time
from bottle import request, abort, response
from libs import Session
from libs.SecretTools import deAES, enAES
from libs.dbAPI import readUsers
from settings import session_timeout

__author__ = 'cyh'


def Xsrf(func):
    def wrapper(*args, **kw):
        req = request.forms.get('token')
        cookie = request.cookies.token
        if req and cookie and req == cookie:
            return func(*args, **kw)
        else:
            abort(403, "Sorry, access denied.")

    return wrapper


def Auth(func):
    def wrapper(*args, **kw):
        users = readUsers()
        cookie_session = request.get_cookie('session')
        guest_session_id = request.get_cookie("guest")
        guest_session = Session.getGuest(guest_session_id)
        private = Session.getGuest_key(guest_session_id, 'privateKey')
        user = None if guest_session is None or 'user' not in guest_session else guest_session['user']

        user_ans = session_ans = de_session = session_id = None
        try:
            if user and cookie_session and private:
                de_session = json.loads(deAES(users[user], cookie_session))
                # 第一层验证 cookie解密
                if user in users and de_session['user'] == user:
                    # 第二层验证 session
                    session_id = de_session['session_id']
                    session = Session.get(user, session_id)
                    # session 时间戳不活跃过期机制
                    if float(de_session['time']) + session_timeout > time.time() and \
                            session and session['user'] == user:
                        user_ans = user
                        session_ans = session

        except Exception:
            response.delete_cookie('guest')
            response.delete_cookie('session')
        temp = func(user=user_ans, session=session_ans, *args, **kw)
        if user_ans:
            de_session['time'] = time.time()
            de_session['session_id'] = Session.update(user, session_id, session_ans)
            encrypted = enAES(users[user], json.dumps(de_session))
            response.set_cookie("session", encrypted, path='/')
        return temp


    return wrapper