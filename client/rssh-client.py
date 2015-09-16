#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
import time
import urllib2
import threading

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
            # parse port
            port = response.read()

            cmd = ''
            # start query output thread

            def queryOutput():
                queryUrl = util.makeQueryUrl(args['addr'], port)
                while cmd != 'q':
                    response = urllib2.urlopen(queryUrl, timeout=5)
                    msg = response.read()
                    if len(msg) == 0:
                        time.sleep(1.0)
                    else:
                        # if len(cmd) > 0 and msg.find(cmd + '\n') > -1:
                        #     msg = msg.replace(cmd + '\n', '')
                        #     cmd = ''
                        sys.stdout.write(msg)
                        sys.stdout.flush()

            t = threading.Thread(target=queryOutput)
            t.start()

            print 'Welcome to ssh %s\n[enter \'q\' to exit]' % args['addr']
            # enter prompt
            while True:
                cmd = raw_input()
                cmdUrl = util.makeCmdUrl(args['addr'], port, cmd)
                response = urllib2.urlopen(cmdUrl, timeout=5)
                if cmd == 'q' or response.code != 200:
                    break

    except Exception, e:
        print 'Error: ' + str(e)


if __name__ == '__main__':
    open_rssh(sys.argv[1:])
