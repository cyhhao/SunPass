# coding:utf8
from email.header import decode_header
from email.parser import Parser
from email.utils import parseaddr
import poplib

__author__ = 'cyh'


def guess_charset(msg):
    # 先从msg对象获取编码:
    charset = msg.get_charset()
    if charset is None:
        # 如果获取不到，再从Content-Type字段获取:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset


class emailPOP():
    def __init__(self, email, password, pop3_server):
        self.pop3_server = pop3_server
        self.email = email
        self.password = password
        self.Create()
        self.Auth()
        self.mails_list = []
        self.split = self.getListLen()
        self.dict = {}
        self.subjectDict = {}
        self.updateList()

    def Create(self):
        self.server = poplib.POP3(self.pop3_server)

    def Auth(self):
        self.server.user(self.email)
        self.server.pass_(self.password)

    def Quit(self):
        self.server.quit()

    def Update(self):
        self.Quit()
        self.Create()
        self.Auth()


    def parser(self, id, lines):
        msg_content = '\r\n'.join(lines)
        msg = Parser().parsestr(msg_content)
        content = {
            'Subject': self.decode_str(msg.get('Subject', '')),
            'From': self.decode_person(msg.get('From', '')),
            'To': self.decode_person(msg.get('To', '')),
        }
        self.dict[id] = content
        return content

    def getEmail_all(self, index):
        resp, lines, octets = self.server.retr(index)
        return lines

    def getEmail_header(self, index):
        resp, lines, octets = self.server.top(index, 0)
        return lines

    def find_by_Subject(self, subject, condition='='):
        if subject in self.subjectDict:
            return self.subjectDict[subject]
        else:
            return None

    def getListLen(self):
        resp, mails_list, octets = self.server.list()
        return len(mails_list)

    def updateList(self):
        self.Update()
        resp, mails_list, octets = self.server.list()
        self.mails_list = mails_list
        length = len(self.mails_list)
        print length
        for i in xrange(self.split, length):
            content = self.parser(self.mails_list[i], self.getEmail_header(self.mails_list[i]))
            print content
            subject = content['Subject']
            subject = subject.strip()
            if subject in self.subjectDict:
                self.subjectDict[subject].append(content)
            else:
                self.subjectDict[subject] = [content]
        self.split = length


    def find(self, signal, condition='=', relation='and'):
        for li in self.mails_list:
            if li in self.dict:
                content = self.dict[li]
            else:
                content = self.parser(li, self.getEmail_header(li))
            if condition == '=':
                flag = False
                for k, v in signal.iter():
                    if relation == 'and':
                        flag = flag and (k in content and content[k] == v)
                    elif relation == 'or':
                        flag = flag or (k in content and content[k] == v)
                if flag:
                    return li
        return None

    def decode_str(self, s):
        value, charset = decode_header(s)[0]
        if charset:
            value = value.decode(charset)
        return value

    def decode_person(self, value):
        hdr, addr = parseaddr(value)
        name = self.decode_str(hdr)
        return {
            "name": name,
            "addr": addr
        }