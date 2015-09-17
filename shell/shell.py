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

import base64
from binascii import hexlify
import getpass
import os
import select
import socket
import sys
import time
import traceback
from paramiko.py3compat import input

import paramiko
# try:
#     import interactive
# except ImportError:
#     from . import interactive
import interactive

sys.path.append('../util')
# from util import output_queue
import output_queue


def manual_auth(transport, username):
    transport.auth_password(username, password)


# setup logging
# paramiko.util.log_to_file('demo.log')

port = int(sys.argv[1])
hostname = 'localhost'
username = 'root'
password = 'letmein'
sshPort = 22


# now connect
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((hostname, sshPort))
except Exception as e:
    msg = '*** Connect failed: ' + str(e)
    output_queue.push(msg)
    print(msg)
    traceback.print_exc()
    sys.exit(1)

try:
    t = paramiko.Transport(sock)
    try:
        t.start_client()
    except paramiko.SSHException:
        msg = '*** SSH negotiation failed.'
        output_queue.push(msg)
        print(msg)
        sys.exit(1)

    try:
        keys = paramiko.util.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
    except IOError:
        try:
            keys = paramiko.util.load_host_keys(os.path.expanduser('~/ssh/known_hosts'))
        except IOError:
            print('*** Unable to open host keys file')
            keys = {}

    # check server's host key -- this is important.
    key = t.get_remote_server_key()
    if hostname not in keys:
        print('*** WARNING: Unknown host key!')
    elif key.get_name() not in keys[hostname]:
        print('*** WARNING: Unknown host key!')
    elif keys[hostname][key.get_name()] != key:
        msg = '*** WARNING: Host key has changed!!!'
        print(msg)
        output_queue.push(msg)
        sys.exit(1)
    else:
        print('*** Host key OK.')

    manual_auth(t, username)
    if not t.is_authenticated():
        msg = '*** Authentication failed. :('
        output_queue.push(msg)
        print(msg)
        t.close()
        sys.exit(1)

    chan = t.open_session()
    chan.get_pty(term='linux')
    chan.invoke_shell()
    print('*** Here we go!\n')

    interactive.interactive_shell(chan, port)
    chan.close()
    t.close()

except Exception as e:
    msg = '*** Caught exception: ' + str(e.__class__) + ': ' + str(e)
    output_queue.push(msg)
    print()
    traceback.print_exc()
    try:
        t.close()
    except:
        pass
    sys.exit(1)
