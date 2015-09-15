#! /usr/bin/python
# -*- coding: utf-8 -*-
from django.http import HttpResponse
from subprocess import Popen
import os
import unittest
import socket
from socket import AF_INET, SOCK_DGRAM, timeout


def rssh_start(request):
    # find available ports for msg
    portIn = findAvailablePort()
    portOut = findAvailablePort(portIn + 1)

    # get pyshell dir
    d = getFileDir(__file__)
    shellDir = getShellDir(d)

    # run shell terminal
    Popen(['python', 'shell.py', str(portIn), str(portOut)], cwd=shellDir)

    # wait shell open ok
    s = socket.socket(AF_INET, SOCK_DGRAM)
    s.bind(('', portOut))
    s.settimeout(5)
    try:
        data, addr = s.recvfrom(1024)
        s.close()
        r = HttpResponse('%d;%d' % (portIn, portOut))
    except timeout:
        r = HttpResponse('connect ssh server timeout')
        r.status = 500

    s.close()
    return r


def rssh_exec(request, portIn, portOut, cmd):
    print '%s %s %s' % (portIn, portOut, cmd)
    cmd = cmd.replace('%20', ' ')

    # recv shell result and send back
    s_out = socket.socket(AF_INET, SOCK_DGRAM)
    s_out.bind(('', int(portOut)))
    s_out.settimeout(1)
    try:
        # send cmd to shell
        s_in = socket.socket(AF_INET, SOCK_DGRAM)
        s_in.sendto(cmd + '\n', ('localhost', int(portIn)))
        msg = ""
        while True:
            try:
                data, addr = s_out.recvfrom(1024)
                msg += data
            except timeout:
                break
        s_out.close()
        # remove cmd echo and prompt
        msg = msg[msg.find('\n')+1:]
        msg = msg[:msg.rfind('\n')]
        r = HttpResponse(msg)
    except timeout:
        r = HttpResponse('connect ssh server timeout')
        r.status = 500
    return r


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
    for i in xrange(1, 4):
        end = curDirPath.rfind('/', 0, end)
    return curDirPath[:end] + '/shell'


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

if __name__ == '__main__':
    unittest.main()
