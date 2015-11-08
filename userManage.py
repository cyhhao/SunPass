# coding:utf8
import hashlib
import json

__author__ = 'cyh'


def check(user):
    if '.' in user or '/' in user:
        return False
    else:
        return True


def addUser(dic):
    username = str(raw_input("""
        UserName:"""))

    if username in dic:
        select = raw_input("""This user already exists , update this user（y/n）？
        :""")
        if select.lower() == 'y':
            pass
        else:
            pass
    elif check(username):
        password = str(raw_input("""
        Password(At least 6):"""))
        if len(password) < 6:
            print 'At least 6...'
            return addUser(dic)
        else:
            ps = hashlib.sha512(hashlib.sha256(password).hexdigest()).hexdigest()
            dic[username] = ps
            print 'add OK'
            return None
    else:
        print 'Wrong UserName'


if __name__ == '__main__':
    dic = {}
    while True:
        select = int(raw_input("""
        1. add User
        2. update User
        3. delete User
        4. exit
        select："""))

        if select == 1:
            open("./users.json", 'w').close()
            input = open("./users.json", "r")
            if input.read() or input.read() != "":
                dic = json.loads(input.read())
            addUser(dic)
            input.close()
            output = open("./users.json", "w")
            output.write(json.dumps(dic))
            output.flush()
            output.close()
        elif select == 2:
            pass
        elif select == 3:
            pass
        else:
            break


