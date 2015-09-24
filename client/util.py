#! /usr/bin/python
# -*- coding: utf-8 -*-
import re
import sys
import unittest


def parseCmdArgs(cmdLine):
    '''
    parse command line arguments.
    cmdLine: '-key1 value1 -key2 value2...'
    return: dictionary object with arg keys and values
    '''

    args = {}
    for i in xrange(len(cmdLine)):
        # find arg start
        if cmdLine[i] == '-' and i > 0 and cmdLine[i - 1] == ' ':
            # find next arg start
            for j in xrange(i + 1, len(cmdLine)):
                if cmdLine[j] == '-' and cmdLine[j - 1] == ' ':
                    break
            if j == len(cmdLine) - 1:
                j = len(cmdLine)
            # parse key and value
            for k in xrange(i + 1, j):
                if cmdLine[k] == ' ':
                    key = cmdLine[i + 1:k]
                    args[key] = cmdLine[k:j].strip()
                    break
            i = j - 1

    return args


class CmdArgError(Exception):

    def __init__(self):
        self.message = 'command arguments format error.'

    def __str__(self):
        return self.message


def makeStartUrl(addr):
    return 'http://%s/rssh/start' % addr


def makeCmdUrl(addr, port, cmd):
    return 'http://%s/rssh/%s/exec/%s' % (addr, port, cmd.replace(' ', '%20'))


def makeQueryUrl(addr, port):
    return 'http://%s/rssh/%s/query' % (addr, port)


def makePutUrl(addr, remote_file, content):
    return 'http://%s/rssh/%s/put/%s' % (addr, remote_file, content)


def makeMd5Url(addr, remote_file):
    return 'http://%s/rssh/%s/md5' % (addr, remote_file)


def splitVTCode(s):
    beg = s.find(chr(27))
    if beg == -1:
        return s, ''
    else:
        # VT_ENDs = ['m', 'c', 'n', 'R', 'h', 'l', '(', ')', 'H', 'A', 'B', 'C', 'D', 'f', 's', 'u', '7', '8', 'r', 'M', 'g', 'K', 'J', 'i', 'p', ]
        VT_ENDs = ['m']
        end = sys.maxint
        for c in VT_ENDs:
            e = s.find(c, beg)
            if e != -1 and e < end:
                end = e
        if end == sys.maxint:
            return s[:beg], s[beg:]
        else:
            return s[:beg], s[end + 1:]


def isFileCmd(cmd):
    p = re.compile('(ge|pu)t[ \t]+-from[ \t]+[^\t\n\r\f\v]+-to[ \t]+[^\t\n\r\f\v]+')
    return p.match(cmd) != None


def hexBitStr(b):
    if b < 10:
        return chr(ord('0') + b)
    else:
        return chr(ord('a') + b - 10)


def encodeChrInHex(c):
    i = ord(c)
    return hexBitStr(int(i / 16)) + hexBitStr(i % 16)


def encodeStrInHex(s):
    hexStr = ''
    for c in s:
        hexStr += encodeChrInHex(c)
    return hexStr


class TestUtil(unittest.TestCase):

    def testParseCmdArgs(self):
        args = parseCmdArgs('x -a 0 -b 1')
        self.assertIn('a', args)
        self.assertIn('b', args)
        self.assertEqual(args['a'], '0')
        self.assertEqual(args['b'], '1')

        args = parseCmdArgs('put -from C:/a b/c-d.py -to /home/x')
        self.assertEqual(args['from'], 'C:/a b/c-d.py')
        self.assertEqual(args['to'], '/home/x')

        args = parseCmdArgs('python rssh-client.py -addr 122.96.128.138:8888 -proxy http://')
        self.assertEqual(args['addr'], '122.96.128.138:8888')
        self.assertEqual(args['proxy'], 'http://')

    def testMakeStartUrl(self):
        addr = '1.1.1.1:80'
        self.assertEqual(makeStartUrl(addr), 'http://1.1.1.1:80/rssh/start')

    def testMakeCmdUrl(self):
        addr = '1.1.1.1:80'
        cmd = 'ls -l'
        port = '1'
        self.assertEqual(makeCmdUrl(addr, port, cmd), 'http://1.1.1.1:80/rssh/1/exec/ls%20-l')

    def testMakeQueryUrl(self):
        addr = '1.1.1.1:80'
        port = '1'
        self.assertEqual(makeQueryUrl(addr, port), 'http://1.1.1.1:80/rssh/1/query')

    def testMakePutUrl(self):
        addr = '1.1.1.1:80'
        remote_file = '/home/a.txt'
        content = 'abc'

        self.assertEqual(makePutUrl(addr, remote_file, content), 'http://1.1.1.1:80/rssh//home/a.txt/put/abc')

    def testMakeMd5Url(self):
        addr = '1.1.1.1:80'
        remote_file = '/home/a.txt'

        self.assertEqual(makeMd5Url(addr, remote_file), 'http://1.1.1.1:80/rssh//home/a.txt/md5')

    def testSplitVTCode(self):
        s = 'abcd'
        self.assertEqual(splitVTCode(s), ('abcd', ''))

        s = 'ab0ab1cd'
        b = bytearray(s)
        b[2] = chr(27)
        b[5] = 'm'
        s = str(b)
        self.assertEqual(splitVTCode(s), ('ab', 'cd'))

        s = 'ab01d'
        b = bytearray(s)
        b[2] = chr(27)
        s = str(b)
        self.assertEqual(splitVTCode(s), ('ab', str(chr(27)) + '1d'))

    def testIsFileCmd(self):
        cmd = 'put -from a -to b'
        self.assertTrue(isFileCmd(cmd))

        cmd = 'put -from C:/a b/c -to /home/ss dd'
        self.assertTrue(isFileCmd(cmd))

        cmd = 'put -from a'
        self.assertFalse(isFileCmd(cmd))

        cmd = 'put -to b'
        self.assertFalse(isFileCmd(cmd))

        cmd = 'get -from a -to b'
        self.assertTrue(isFileCmd(cmd))

        cmd = 'get -from C:/a b/c -to /home/ss dd'
        self.assertTrue(isFileCmd(cmd))

        cmd = 'get -from a'
        self.assertFalse(isFileCmd(cmd))

        cmd = 'get -to b'
        self.assertFalse(isFileCmd(cmd))

    def testEncodeHexStr(self):
        self.assertEqual(encodeChrInHex(chr(0)), '00')
        self.assertEqual(encodeChrInHex(chr(8)), '08')
        self.assertEqual(encodeChrInHex('1'), '31')
        self.assertEqual(encodeChrInHex('A'), '41')
        self.assertEqual(encodeChrInHex(chr(126)), '7e')

        self.assertEqual(encodeStrInHex('A\x001'), '410031')

if __name__ == '__main__':
    # import unicodedata
    # x = chr(27) + '[' + chr(0) + 'm'
    # print 'x before: ' + x
    # x = unicodedata.normalize('NFKD', x.decode('utf-8')).encode('ascii', 'ignore')
    # print 'x after: ' + x
    # sys.stdout.write('\x1b[\x00m\x1b[\x01;\x22mredis-3.0.4\x1b[\x00m\n')
    # sys.stdout.flush()
    unittest.main()
