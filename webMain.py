# coding:utf8
import hashlib
import json
import random
import time

import rsa

from libs import Session
from libs.Middleware import Xsrf, Auth
from libs.SecretTools import deRSA, enRSA, createRSA, enAES
from libs.dbAPI import savePassword, readUsers, loadPassword, makeDir
from settings import port


__author__ = 'cyh'
from bottle import route, run, view, static_file, post, request, response


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


if __name__ == '__main__':
    makeDir()
    readUsers()
    run(host='127.0.0.1', port=port)
