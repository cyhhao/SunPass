# dict = {'Name': 'Zara', 'Age': 7}
# dict2 = {'Sex': 'female', 'Age': 8}
#
# dict.update(dict2)
# print "Value : %s" % dict


def splitStr(message, length):
    return [message[i * length:(i + 1) * length] for i in xrange(len(message) / length + 1)]


print splitStr('1234567890a', 14)
print 'abc'[2:5]