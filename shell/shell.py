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
from socket import AF_INET, SOCK_DGRAM, timeout

import paramiko
try:
    import interactive
except ImportError:
    from . import interactive


def agent_auth(transport, username):
    """
    Attempt to authenticate to the given transport using any of the private
    keys available from an SSH agent.
    """

    agent = paramiko.Agent()
    agent_keys = agent.get_keys()
    if len(agent_keys) == 0:
        return

    for key in agent_keys:
        print('Trying ssh-agent key %s' % hexlify(key.get_fingerprint()))
        try:
            transport.auth_publickey(username, key)
            print('... success!')
            return
        except paramiko.SSHException:
            print('... nope.')


def manual_auth(transport, username):
    transport.auth_password(username, password)


# setup logging
paramiko.util.log_to_file('demo.log')

portIn = int(sys.argv[1])
portOut = int(sys.argv[2])
hostname = 'localhost'
username = 'root'
password = 'letmein'
sshPort = 22

# now connect
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((hostname, sshPort))
except Exception as e:
    print('*** Connect failed: ' + str(e))
    traceback.print_exc()
    sys.exit(1)

try:
    t = paramiko.Transport(sock)
    try:
        t.start_client()
    except paramiko.SSHException:
        print('*** SSH negotiation failed.')
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
        print('*** WARNING: Host key has changed!!!')
        sys.exit(1)
    else:
        print('*** Host key OK.')

    agent_auth(t, username)
    if not t.is_authenticated():
        manual_auth(t, username)
    if not t.is_authenticated():
        print('*** Authentication failed. :(')
        t.close()
        sys.exit(1)

    chan = t.open_session()
    chan.get_pty()
    chan.invoke_shell()
    print('*** Here we go!\n')

    # tell site conn ok
    time.sleep(1)
    s = socket.socket(AF_INET, SOCK_DGRAM)
    s.sendto('connect ok', ('localhost', portOut))

    interactive.interactive_shell(chan, portIn, portOut)
    chan.close()
    t.close()

except Exception as e:
    print('*** Caught exception: ' + str(e.__class__) + ': ' + str(e))
    traceback.print_exc()
    try:
        t.close()
    except:
        pass
    sys.exit(1)
