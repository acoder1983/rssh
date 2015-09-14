#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
import urllib2

import util


def open_rssh(cmdArgs):
    '''
    cmdArgs: -addr [ip:port] -proxy [proxy_addr]
    '''
    try:
        # parse cmdArgs
        args = util.parseCmdArgs(cmdArgs)
        if 'addr' not in args:
            print 'need \'-addr [ip:port]\''
            return

        # start rssh
        startUrl = util.makeStartUrl(args['addr'])
        response = urllib2.urlopen(startUrl, timeout=10)

        if response.code == 200:
            # parse portIn and portOut
            msg = response.read()
            ports = msg.split(';')

            print 'Welcome to ssh %s\n[enter \'q\' to exit]' % args['addr']
            # enter prompt
            while True:
                cmd = raw_input('>>')
                cmdUrl = util.makeCmdUrl(args['addr'], ports[0], ports[1], cmd)
                response = urllib2.urlopen(cmdUrl, timeout=5)
                print response.read()
                if cmd == 'q' or response.code != 200:
                    break
    except Exception, e:
        print 'Error: ' + str(e)


if __name__ == '__main__':
    open_rssh(sys.argv[1:])
