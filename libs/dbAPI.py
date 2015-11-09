# coding:utf8
import hashlib
import json

__author__ = 'cyh'

users_path = './users.json'


def savePassword(user, allPass):
    if not checkName(user):
        return None

    with open('./password/%s.json' % user, 'w') as file:
        text = json.dumps(allPass)
        file.write(text)
        file.flush()


def readUsers():
    try:
        file = open(users_path, 'r')
        users = json.loads(file.read())
        file.close()
        return users
    except Exception:
        return {}


def saveUsers(users):
    try:
        file = open(users_path, 'w')
        file.write(json.dumps(users))
        file.flush()
        file.close()
        return True
    except Exception:
        return False


def addUser(username, password, override=False):
    users = readUsers()
    if username in users and not override:
        return False, "This user already exists"
    else:
        (flag, msg) = checkName(username)
        if not flag:
            return flag, msg
        (flag, msg) = checkPassword(password)
        if not flag:
            return flag, msg
        # 对密码进行两次Hash
        # 第一次为sha256 , 第二次为sha512
        ps = hashlib.sha512(hashlib.sha256(password).hexdigest()).hexdigest()
        users[username] = ps

        flag = saveUsers(users)
        if not flag:
            return flag, "Save File Error"
        return True, "Succeed"


def updateUser(username, password):
    users = readUsers()
    if username in users:
        return addUser(username, password, True)
    else:
        return False, "This user is not exists ."


def deleteUser(username):
    users = readUsers()
    if username in users:
        del users[username]
        flag = saveUsers(users)
        if not flag:
            return flag, "Save File Error"
        return True, "Succeed"
    else:
        return False, "This user is not exists ."


def loadPassword(user):
    if not checkName(user):
        return None
    try:
        with open('./password/%s.json' % user, 'r') as file:
            text = file.read()
            allPass = json.loads(text)
            return allPass
    except Exception, e:
        print Exception, e
        return {}


def checkName(user):
    if user is None or len(user) < 3:
        return False, "Wrong UserName , it's too short ."
    if '.' in user or '/' in user:
        return False, "Wrong UserName , it can't include '.' and '/' ."
    else:
        return True, "ok"


def checkPassword(password):
    if password is None or len(password) < 6:
        return False, "Password is too sort (At least 6...)"
    return True, "ok"
