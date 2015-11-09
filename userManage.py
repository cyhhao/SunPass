# coding:utf8
import getopt
import hashlib
import json
import os
import sys

from libs.dbAPI import checkName, addUser, updateUser, deleteUser, readUsers, makeDir


__author__ = 'cyh'


def add(username, password):
    (flag, msg) = addUser(username, password)
    if not flag:
        print "Error: ", msg
    else:
        print msg


def update(username, password):
    (flag, msg) = updateUser(username, password)
    if not flag:
        print "Error: ", msg
    else:
        print msg


def delete(username):
    (flag, msg) = deleteUser(username)
    if not flag:
        print "Error: ", msg
    else:
        print msg


def listUsers():
    users = readUsers()
    for i, user in enumerate(users.keys()):
        print i + 1, ":", user


def control():
    while True:
        try:
            select = int(raw_input("""
            0. list All User
            1. add User
            2. update User
            3. delete User
            4. exit
            select: """))
            if select == 0:
                listUsers()
            elif select == 1:
                username = str(raw_input("UserName:"))
                password = str(raw_input("Password(At least 6):"))
                add(username, password)
            elif select == 2:
                username = str(raw_input("UserName:"))
                password = str(raw_input("Password(At least 6):"))
                update(username, password)
            elif select == 3:
                username = str(raw_input("UserName:"))
                delete(username)
            else:
                break
            raw_input("Press Enter to continue ... ")
        except Exception:
            pass


if __name__ == '__main__':
    makeDir()
    help = """
    python userManage.py [option][value]...

    -u or --user [value] (user's name)
    -p or --password [value] (user's password)
    (-u xxx -p ****** to add a new user)

    -d or --delete (user's name) delete a user
    -s or --show (show all of user)
    -c or (None) (show menu to manage users)
    -h or --help (show this)
    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:p:d:sc", ["help", "user", "password", "delete", "show"])
    except getopt.GetoptError, err:
        print str(err)
        sys.exit(2)
    isControl = True
    isDelete = False
    user = password = None
    for o, a in opts:
        if o in ("-h", "--help"):
            print help
            sys.exit()
        elif o in ("-u", "--user"):
            user = str(a)
            isControl = False
        elif o in ("-p", "--password"):
            password = str(a)
            isControl = False
        elif o in ("-d", "--delete"):
            user = str(a)
            isDelete = True
            isControl = False
        elif o in ("-s", "--show"):
            listUsers()
            sys.exit()
        elif o in ("-c",):
            control()
            sys.exit()
        else:
            assert False, "unhandled option"

    if isControl:
        control()
        sys.exit()

    if isDelete:
        (flag, msg) = deleteUser(user)
        if not flag:
            print "Error: ", msg
        else:
            print msg
    else:
        if user is None or password is None:
            print "Error: ", "please input -u xxx -p ******"
            sys.exit()
        add(user, password)