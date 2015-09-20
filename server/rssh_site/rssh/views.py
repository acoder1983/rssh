#! /usr/bin/python
# -*- coding: utf-8 -*-
from django.http import HttpResponse
from subprocess import Popen
import os
import re
import sys
import unittest
import socket
from socket import AF_INET, SOCK_DGRAM, timeout

sys.path.append('/home/rssh/util')
# from util import output_queue
import output_queue


def rssh_start(request):
    # find available ports for msg
    port = findAvailablePort()

    # get pyshell dir
    d = getFileDir(__file__)
    shellDir = getShellDir(d)

    # run shell terminal
    output_queue.clear()
    Popen(['python', 'shell.py', str(port)], cwd=shellDir)

    r = HttpResponse('%d' % port)

    return r


def rssh_exec(request, port, cmd):
    cmd = cmd.replace('%20', ' ')

    try:
        # send cmd to shell
        s_in = socket.socket(AF_INET, SOCK_DGRAM)
        if startWithlsCmd(cmd):
            # remove escape sequence
            cmd += '|cat'
        s_in.sendto(cmd + '\n', ('localhost', int(port)))
        r = HttpResponse()
    except Exception, e:
        r = HttpResponse(str(e))
        r.status = 500
    return r


def rssh_query(request, port):
    # fetch outputs
    msg = ''
    for x in xrange(5):
        s = output_queue.pop()
        if s:
            msg += s
        else:
            break

    # send back
    return HttpResponse(msg)


def findAvailablePort(startPort=19831):
    for port in range(startPort, 65536):
        if canBindPort(port):
            return port


def canBindPort(port):
    s = socket.socket(AF_INET, SOCK_DGRAM)
    try:
        s.bind(('', port))
        s.close()
        return True
    except socket.error:
        return False


def getFileDir(filePath):
    return os.path.dirname(os.path.abspath(filePath))


def getShellDir(curDirPath):
    end = len(curDirPath)
    for i in xrange(3):
        end = curDirPath.rfind('/', 0, end)
    return curDirPath[:end] + '/shell'


def getUtilDir():
    curDirPath = getFileDir(__file__)
    end = len(curDirPath)
    for i in xrange(3):
        end = curDirPath.rfind('/', 0, end)
    return curDirPath[:end] + '/util'


def startWithlsCmd(cmd):
    p = re.compile('l[ls]')
    return p.match(cmd) != None


class TestView(unittest.TestCase):

    def testCanBindPort(self):
        port = 61983
        s = socket.socket(AF_INET, SOCK_DGRAM)
        s.bind(('', port))

        self.assertFalse(canBindPort(port))
        s.close()
        self.assertTrue(canBindPort(port))

    def testGetShellDir(self):
        curDirPath = '/a/b/c/d'
        self.assertEqual(getShellDir(curDirPath), '/a/shell')

    def testStartWithlsCmd(self):
        cmd = 'ls'
        self.assertTrue(startWithlsCmd(cmd))

        cmd = 'll'
        self.assertTrue(startWithlsCmd(cmd))

        cmd = 'ls -a'
        self.assertTrue(startWithlsCmd(cmd))

        cmd = 'll   --author'
        self.assertTrue(startWithlsCmd(cmd))

        cmd = 'l'
        self.assertFalse(startWithlsCmd(cmd))

        cmd = 'a'
        self.assertFalse(startWithlsCmd(cmd))

        cmd = 'lstate'
        self.assertFalse(startWithlsCmd(cmd))

        cmd = 'llok'
        self.assertFalse(startWithlsCmd(cmd))

if __name__ == '__main__':
    unittest.main()
