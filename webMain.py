# coding:utf8
import hashlib
import json
import random
import time
import rsa
from libs import Session
from libs.Middleware import Xsrf, Auth
from libs.SecretTools import deRSA, enRSA, createRSA, enAES
from libs.dbAPI import savePassword, readUsers, loadPassword, makeDir, checkName, checkPassword, addUser
from libs.geetest import geetest
from settings import port, captcha_id, private_key


__author__ = 'cyh'
from bottle import route, run, view, static_file, post, request, response

gt = None


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
        # response.delete_cookie("guest")
    response.set_cookie("guest", new_guest, path='/')
    return dict(title=title, user=user, publickey=public, versions=1)


@route('/register')
@view('register')
def register():
    response.set_cookie("token", str(random.random()), path='/')
    (public, private) = createRSA()
    guest = request.get_cookie("guest")

    new_guest = Session.updateGuest(guest, {'privateKey': private})
    response.set_cookie("guest", new_guest, path='/')
    return dict(title="Register",
                publickey=public,
                versions=1,
                GeetestParam={
                    "id": captcha_id,
                    "challenge": gt.geetest_register()
                })


@post('/ajax/register')
@Xsrf
def registerAjax():
    users = readUsers()
    user = request.forms.get('user')
    password = request.forms.get('password')

    challenge = request.forms.get('validate[geetest_challenge]')
    validate = request.forms.get('validate[geetest_validate]')
    seccode = request.forms.get('validate[geetest_seccode]')

    result = gt.geetest_validate(challenge, validate, seccode)
    if not result:
        return resJSON(0, "Validate Fail ")

    guest_session_id = request.get_cookie("guest")
    private = Session.getGuest_key(guest_session_id, 'privateKey')

    try:
        de_user = deRSA(user, private)
        de_password = deRSA(password, private)


        flag, msg = addUser(de_user, de_password, False)

        if flag:
            return resJSON(1, msg)
        else:
            return resJSON(0, msg)

    except Exception, e:
        print e
    return resJSON(0, "Username or Password is Wrong")


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
        print de_user, de_password
        print users[de_user]

        if de_user in users and users[de_user] == de_password:
            session_id = Session.set(de_user, None, {"user": de_user})
            encrypted = enAES(de_password, json.dumps({"user": de_user, "time": time.time(), "session_id": session_id}))
            new_guest = Session.updateGuest(guest_session_id, {'user': de_user})
            response.set_cookie("guest", new_guest, path='/')
            response.set_cookie("session", encrypted, path='/')
            return resJSON(1, "ok")
    except Exception, e:
        print e
    return resJSON(0, "Username or Password is Wrong")


@post('/ajax/getPass')
@Auth
@Xsrf
def getPass(user, session):
    users = readUsers()
    if user and user in users:
        n = request.forms.n
        e = request.forms.e
        publicKey = rsa.PublicKey(int(n), int(e))
        allPass = loadPassword(user)
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
    try:
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
    except Exception:
        print Exception

    return resJSON(0, "Error. try refresh the page")


@post('/ajax/deletePass')
@Auth
@Xsrf
def deletePass(user, session):
    users = readUsers()

    try:
        if user and user in users:
            id = request.forms.id
            allPass = loadPassword(user)
            if id in allPass:
                del allPass[id]
                savePassword(user, allPass)
                return resJSON(1, "delete ok")
            else:
                return resJSON(1, "delete already")
    except Exception:
        print Exception

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


if __name__ == '__main__':
    makeDir()
    readUsers()
    gt = geetest(captcha_id, private_key)
    run(host='127.0.0.1', port=port)
