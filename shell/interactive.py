#! /usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2003-2007  Robey Pointer <robeypointer@gmail.com>
#
# This file is part of paramiko.
#
# Paramiko is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# Paramiko is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Paramiko; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA.


import socket
import sys
import unicodedata
from paramiko.py3compat import u

# windows does not have termios...
try:
    import termios
    import tty
    has_termios = True
except ImportError:
    has_termios = False


def interactive_shell(chan, portIn, portOut):
    if has_termios:
        posix_shell(chan, portIn, portOut)
    else:
        # windows_shell(chan)
        print 'not support posix_shell'
        sys.exit(1)


def posix_shell(chan, portIn, portOut):
    import select

    oldtty = termios.tcgetattr(sys.stdin)

    s_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_in.bind(('', portIn))

    try:
        tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        chan.settimeout(0.0)

        while True:
            r, w, e = select.select([chan, sys.stdin, s_in], [], [])
            if chan in r:
                try:
                    x = u(chan.recv(1024))
                    x = unicodedata.normalize('NFKD', x).encode('ascii', 'ignore')
                    if len(x) == 0:
                        s_in.close()
                        sys.stdout.write('\r\n*** EOF\r\n')
                        break
                    sys.stdout.write(x)
                    sys.stdout.flush()

                    # send back
                    host = 'localhost'
                    s_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s_out.sendto(x, (host, portOut))

                except socket.timeout:
                    pass
            if sys.stdin in r:
                x = sys.stdin.read(1)
                if len(x) == 0:
                    break
                chan.send(x)
            if s_in in r:
                data, addr = s_in.recvfrom(1024)
                if data == 'q\n':
                    data = 'exit\n'
                chan.send(data)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)


# thanks to Mike Looijmans for this code
def windows_shell(chan):
    import threading

    sys.stdout.write("Line-buffered terminal emulation. Press F6 or ^Z to send EOF.\r\n\r\n")

    def writeall(sock):
        while True:
            data = sock.recv(256)
            if not data:
                sys.stdout.write('\r\n*** EOF ***\r\n\r\n')
                sys.stdout.flush()
                break
            sys.stdout.write(data)
            sys.stdout.flush()

    writer = threading.Thread(target=writeall, args=(chan,))
    writer.start()

    try:
        while True:
            d = sys.stdin.read(1)
            if not d:
                break
            chan.send(d)
    except EOFError:
        # user hit ^Z or F6
        pass


def replaceUnicode(s, replaceChar):
    '''
    用指定字符替换字符串内的unicode字符
    s：需要进行替换的字符串
    replaceChar：替换unicode的ascii字符
    return：替换后的str
    '''
    ba = bytearray(s)
    for x in range(0, len(ba)):
        if ba[x] > 127:
            ba[x] = ord(replaceChar)
    return str(ba)
