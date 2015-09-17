import urllib2


def getInternetIp():

    urls = ['http://1111.ip138.com/ic.asp',
            'http://www.ip.cn', ]
    tags = [['[', ']'],
            ['', '']]

    for i in range(0, len(urls)):
        try:
            ip = getIp(urls[i], tags[i][0], tags[i][1])
            return ip
        except Exception, e:
            print str(e)
            

def getIp(url, tagBeg, tagEnd):

    r = urllib2.urlopen(url)
    c = r.read()
    beg = c.index(tagBeg) + len(tagBeg)
    end = c.index(tagEnd)
    return c[beg:end]

if __name__ == '__main__':
    print getInternetIp()
