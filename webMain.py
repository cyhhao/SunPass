# coding:utf8
import base64
import hashlib
import json
import random
from Crypto.Cipher import AES
import rsa
import time
import Session
from userManage import check

__author__ = 'cyh'
from bottle import route, run, view, static_file, post, request, response, abort

session_timeout = 600


def _splitStr(message, length):
    return [message[i * length:(i + 1) * length] for i in xrange(len(message) / length + 1)]


def deRSA(input, privkey):
    return ''.join([rsa.decrypt(base64.b64decode(str(etext)), privkey) for etext in input.split('|')])


def enRSA(input, public):
    return '|'.join([base64.b64encode(rsa.encrypt(text, public)) for text in _splitStr(input, 117)])


def createRSA():
    (pubkey, privkey) = rsa.newkeys(1024)
    pubkeyStr = hex(pubkey.n)[2:-1] + "|" + str(hex(pubkey.e))[2:]
    return pubkeyStr, privkey


def sha2key(key):
    key = base64.b64encode(key)
    if len(key) > 32:
        key = key[:32]
    return key.zfill(32)


"""
AES 加密专用
"""
BS = AES.block_size
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[0:-ord(s[-1])]


def deAES(key, text):
    cipher = AES.new(sha2key(key))
    return unpad(cipher.decrypt(base64.b64decode(text)))


def enAES(key, text):
    cipher = AES.new(sha2key(key))
    return base64.b64encode(cipher.encrypt(pad(text)))


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
        user = None if guest_session is None or 'user'not in guest_session else guest_session['user']

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


def resJSON(status, msg="", data=None):
    res = {
        'code': status,
        'msg': msg
    }
    if data:
        res['data'] = data
    return json.dumps(res)


@route('/static/<filename:path>')
def server_static(filename):
    return static_file(filename, root='./static')


@route('/')
@view('hello')
@Auth
def index(user, session):
    response.set_cookie("token", str(random.random()), path='/')
    (public, private) = createRSA()
    guest = request.get_cookie("guest")
    new_guest = Session.updateGuest(guest, {'privateKey': private})


    if user is not None:
        title = 'Hello %s !' % user
    else:
        title = 'Hello !'
        #response.delete_cookie("guest")
    response.set_cookie("guest", new_guest, path='/')
    return dict(title=title, user=user, publickey=public)


@post('/ajax/login')
@Xsrf
def login():
    users = readUsers()
    user = request.forms.get('user')
    password = request.forms.get('password')
    guest_session_id = request.get_cookie("guest")
    private = Session.getGuest_key(guest_session_id, 'privateKey')
    try:
        de_user = deRSA(user, private)
        de_password = deRSA(password, private)
        de_password = hashlib.sha512(de_password).hexdigest()

        if de_user in users and users[de_user] == de_password:
            session_id = Session.set(de_user, None, {"user": de_user})
            encrypted = enAES(de_password, json.dumps({"user": de_user, "time": time.time(), "session_id": session_id}))
            new_guest = Session.updateGuest(guest_session_id, {'user': de_user})
            response.set_cookie("guest", new_guest, path='/')

            response.set_cookie("session", encrypted, path='/')
            return resJSON(1, "ok")
    except Exception:
        print Exception
    return resJSON(0, "Username or Password is Wrong")


@post('/ajax/getPass')
@Auth
@Xsrf
def getPass(user, session):
    users = readUsers()
    print "user:", user
    if user and user in users:
        n = request.forms.n
        e = request.forms.e
        publicKey = rsa.PublicKey(int(n), int(e))
        allPass = loadPassword(user)
        print allPass
        message = json.dumps(allPass)
        after = enRSA(message, publicKey)
        return resJSON(1, "ok", after)
    return resJSON(0, "no")


@post('/ajax/editPass')
@Auth
@Xsrf
def editPass(user, session):
    users = readUsers()
    guest_key = request.get_cookie("guest")

    private = Session.getGuest_key(guest_key, 'privateKey')
    # try:
    if user and user in users and private:
        item = request.forms.item
        item = deRSA(item, private)

        item = item.split("|")
        id = item[1]
        value = item[0]

        allPass = loadPassword(user)

        allPass[id] = value
        savePassword(user, allPass)

        return resJSON(1, "save ok")
    # except Exception:
    # print Exception

    return resJSON(0, "Error. try refresh the page")

@post('/ajax/deletePass')
@Auth
@Xsrf
def deletePass(user, session):
    users = readUsers()

    # try:
    if user and user in users:
        id = request.forms.id
        allPass = loadPassword(user)
        if id in allPass:
            del allPass[id]
            savePassword(user, allPass)
            return resJSON(1, "delete ok")
        else:
            return resJSON(1, "delete already")
    # except Exception:
    # print Exception

    return resJSON(0, "Error. try refresh the page")


@post('/logout')
@Auth
@Xsrf
def deletePass(user, session):
    guest_session_id = request.get_cookie("guest")
    Session.deleteGuest(guest_session_id)
    response.delete_cookie("guest")
    response.delete_cookie("token")
    response.delete_cookie("session")
    return resJSON(1, "bye")


def loadPassword(user):
    if not check(user):
        return None
    try:
        with open('./password/%s.json' % user, 'r') as file:
            text = file.read()
            allPass = json.loads(text)
            return allPass
    except Exception, e:
        print Exception, e
        return {}

    return None


def savePassword(user, allPass):
    if not check(user):
        return None

    with open('./password/%s.json' % user, 'w') as file:
        text = json.dumps(allPass)
        file.write(text)
        file.flush()


def readUsers():
    with open('./users.json', 'r') as file:
        users = json.loads(file.read())
        file.close()
        return users


if __name__ == '__main__':
    readUsers()
    run(host='localhost', port=80)
