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

sys.path.append('../util')
# from util import output_queue
import output_queue


def interactive_shell(chan, port):
    if has_termios:
        posix_shell(chan, port)
    else:
        # windows_shell(chan)
        print 'not support posix_shell'
        sys.exit(1)


def posix_shell(chan, port):
    import select

    oldtty = termios.tcgetattr(sys.stdin)

    s_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_in.bind(('', port))

    try:
        tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        chan.settimeout(0.0)

        while True:
            r, w, e = select.select([chan, sys.stdin, s_in], [], [])
            if chan in r:
                try:
                    x = u(chan.recv(1024))
                    if len(x) == 0:
                        s_in.close()
                        sys.stdout.write('\r\n*** EOF\r\n')
                        break
                    # encode msg in ascii
                    x = unicodedata.normalize('NFKD', x).encode('ascii', 'ignore')
                    sys.stdout.write(x)
                    sys.stdout.flush()

                    # send back
                    output_queue.push(x)

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
