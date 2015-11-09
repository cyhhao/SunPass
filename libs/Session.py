# coding:utf8
import hashlib
import random
import time

dict = {}


def _set(key, value):
    dict[key] = value


def _get(key):
    if key in dict:
        return dict[key]
    else:
        return None


def set(user, old_id, value):
    if old_id:
        del dict[user + old_id]
    session_id = str(hashlib.sha512(str(random.random())))
    _set(user + session_id, value)
    return session_id


def get(user, session_id):
    return _get(user + session_id)


def update(user, old_id, value=None):
    if not value:
        value = get(user, old_id)
    return set(user, old_id, value)


def setGuest(value):
    key = hashlib.sha512(str(random.random())).hexdigest()
    if value is None:
        value = {}
    value["_time"] = time.time()
    dict[key] = value
    return key


def getGuest(key):
    tmp = _get(key)
    return tmp


def getGuest_key(guest_key, dict_key):
    guest = getGuest(guest_key)
    if guest and dict_key in guest:
        return guest[dict_key]
    else:
        return None


def updateGuest(key, value=None):
    tmp = getGuest(key)
    deleteGuest(key)
    if tmp is None:
        tmp = {}
    if value:
        tmp.update(value)
    return setGuest(tmp)


def deleteGuest(key):
    if key in dict:
        del dict[key]