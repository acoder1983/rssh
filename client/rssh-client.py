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
                tmp = ''
                while cmd != 'q' and cmd != 'exit':
                    try:
                        response = urllib2.urlopen(queryUrl, timeout=5)
                        msg = response.read()
                        if len(msg) == 0:

                            time.sleep(3.0)
                        else:
                            # remove vt100 ctrl code (027~m)
                            # tmp += msg
                            # while True:
                            #     hasSplit, tmp = util.splitVTCode(tmp)
                            #     if len(hasSplit) == 0:
                            #         break
                            #     else:
                            #         for c in hasSplit:
                            #             if ord(c) == 13:
                            #                 continue
                            #             sys.stdout.write(c)
                            #             sys.stdout.flush()
                            # bs = bytearray(msg)
                            # for b in bs:
                            #     sys.stdout.write(str(int(b))+str(chr(b)))
                            #     sys.stdout.flush()
                            for c in msg:
                                if ord(c) == 13:
                                    continue
                                    # c = chr(10)
                                    # print ''
                                    # continue
                                    # time.sleep(3)
                                s = c + ' ' + str(ord(c)) + ' '
                                sys.stdout.write(s)
                                sys.stdout.flush()
                            # sys.stdout.write(msg)
                            # sys.stdout.flush()

                    except Exception, e:
                        print str(e)

            t = threading.Thread(target=queryOutput)
            t.start()

            print 'Welcome to ssh %s\n[enter \'q\' to exit]' % args['addr']
            # enter prompt
            while True:
                cmd = raw_input()
                cmdUrl = util.makeCmdUrl(args['addr'], port, cmd)
                response = urllib2.urlopen(cmdUrl, timeout=5)
                if cmd == 'q' or cmd == 'exit' or response.code != 200:
                    break

    except Exception, e:
        print 'Error: ' + str(e)


if __name__ == '__main__':
    open_rssh(sys.argv[1:])
