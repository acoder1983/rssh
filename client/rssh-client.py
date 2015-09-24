#! /usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import time
import hashlib
import urllib2
import threading

import util

EXIT_RSSH_CMD = 'qq'  # exit rssh session cmd, not using exit, q , quit


def open_rssh(cmdArgs):
    '''
    cmdArgs: -addr [ip:port] -proxy [proxy_addr]
    '''
    try:
        # parse cmdArgs
        args = util.parseCmdArgs(' '.join(cmdArgs))
        if 'addr' not in args:
            print 'need \'-addr [ip:port]\''
            return

        # start rssh
        if 'proxy' in args:
            proxyConfig = args['proxy']
            opener = urllib2.build_opener(urllib2.ProxyHandler({'http': proxyConfig}))
            urllib2.install_opener(opener)
        startUrl = util.makeStartUrl(args['addr'])
        response = urllib2.urlopen(startUrl, timeout=10)

        if response.code == 200:
            # parse port
            port = response.read()
            # validate port format
            port_int = int(port)
            port = str(port_int)

            cmd = ''
            # start query output thread

            def queryOutput():
                queryUrl = util.makeQueryUrl(args['addr'], port)
                tmp = ''
                while cmd != EXIT_RSSH_CMD:
                    try:
                        response = urllib2.urlopen(queryUrl, timeout=5)
                        msg = response.read()
                        if len(msg) == 0:
                            time.sleep(3.0)
                        else:
                            # remove vt100 ctrl code (027~m)
                            tmp += msg
                            while True:
                                hasSplit, tmp = util.splitVTCode(tmp)
                                if len(hasSplit) == 0:
                                    break
                                else:
                                    for c in hasSplit:
                                        if ord(c) == 13:
                                            # skip extra carriage for not line delete
                                            continue
                                        sys.stdout.write(c)
                                        sys.stdout.flush()

                    except Exception, e:
                        print str(e)
                        time.sleep(3.0)

            def putFile(local, remote):
                try:
                    # read local file
                    f = open(local, 'rb')
                    bs = f.read()

                    # check md5
                    local_md5 = hashlib.md5()
                    local_md5.update(bs)
                    local_md5 = local_md5.hexdigest()

                    url = util.makeMd5Url(args['addr'], remote)
                    response = urllib2.urlopen(url, timeout=5)
                    if response.code == 200:
                        remote_md5 = response.read()
                        if remote_md5 != local_md5:
                            # send file bytes
                            filesize = len(bs)
                            sendsize = 0
                            packsize = 50
                            while sendsize < filesize:
                                content = util.encodeStrInHex(bs[sendsize:sendsize + packsize])
                                url = util.makePutUrl(args['addr'], remote, content)
                                response = urllib2.urlopen(url, timeout=5)
                                if response.code != 200:
                                    break
                                sendsize += packsize
                                sys.stdout.write('%d%%.' % int(sendsize * 100 / filesize))

                            # check md5
                            url = util.makeMd5Url(args['addr'], remote)
                            response = urllib2.urlopen(url, timeout=5)
                            if response.code == 200:
                                remote_md5 = response.read()
                                if remote_md5 != local_md5:
                                    print 'put file failed. md5 not equal.'
                                else:
                                    print 'put file ok.'
                            else:
                                print response.read()
                        else:
                            print 'files are identical.'
                    else:
                        print response.read()

                except Exception, e:
                    print str(e)

            workThread = threading.Thread(target=queryOutput)
            workThread.start()

            print '[rssh] Welcome to ssh %s\n[rssh] remote port is %s\n[rssh] enter \'%s\' to exit\n' % (args['addr'], port, EXIT_RSSH_CMD)
            # enter prompt
            while True:
                cmd = raw_input()
                # get cmd: get -from [remote file] -to [local file]
                # put cmd: put -from [local file] -to [remote file]
                if util.isFileCmd(cmd):
                    putCmd = cmd
                    # stop output thread
                    cmd = EXIT_RSSH_CMD
                    workThread.join()
                    # start put thread
                    cmd = putCmd
                    args = util.parseCmdArgs(cmd)
                    workThread = threading.Thread(target=putFile, args=(args['from'], args['to']))
                    workThread.start()
                cmdUrl = util.makeCmdUrl(args['addr'], port, cmd)
                response = urllib2.urlopen(cmdUrl, timeout=5)
                if cmd == EXIT_RSSH_CMD or response.code != 200:
                    break

    except Exception, e:
        print 'Error: ' + str(e)


if __name__ == '__main__':
    open_rssh(sys.argv)
