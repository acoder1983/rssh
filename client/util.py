#! /usr/bin/python
# -*- coding: utf-8 -*-
import unittest


def parseCmdArgs(cmdArgs):
    '''
    parse command line arguments.
    cmdArgs: [-key, value, -key, value...]
    return: dictionary object with arg keys and values
    '''
    if len(cmdArgs) % 2 == 1:
        raise CmdArgError
    args = {}
    for i in range(0, len(cmdArgs), 2):
        if not cmdArgs[i].startswith('-'):
            raise CmdArgError
        args[cmdArgs[i][1:]] = cmdArgs[i + 1]

    return args


class CmdArgError(Exception):

    def __init__(self):
        self.message = 'command arguments format error.'

    def __str__(self):
        return self.message


def makeStartUrl(addr):
    return 'http://%s/rssh/start' % addr


def makeCmdUrl(addr, port, cmd):
    return 'http://%s/rssh/%s/exec/%s' % (addr, port, cmd.replace(' ', '%20'))


def makeQueryUrl(addr, port):
    return 'http://%s/rssh/%s/query' % (addr, port)


class TestUtil(unittest.TestCase):

    def testParseCmdArgs(self):
        args = parseCmdArgs(['-a', '0', '-b', '1'])
        self.assertIn('a', args)
        self.assertIn('b', args)
        self.assertEqual(args['a'], '0')
        self.assertEqual(args['b'], '1')

    def testParseInvalidCmdArgs(self):
        with self.assertRaises(CmdArgError):
            parseCmdArgs(['-a'])

        with self.assertRaises(CmdArgError):
            parseCmdArgs(['a', '0'])

    def testMakeStartUrl(self):
        addr = '1.1.1.1:80'
        self.assertEqual(makeStartUrl(addr), 'http://1.1.1.1:80/rssh/start')

    def testMakeCmdUrl(self):
        addr = '1.1.1.1:80'
        cmd = 'ls -l'
        port = '1'
        self.assertEqual(makeCmdUrl(addr, port, cmd), 'http://1.1.1.1:80/rssh/1/exec/ls%20-l')

    def testMakeQueryUrl(self):
        addr = '1.1.1.1:80'
        port = '1'
        self.assertEqual(makeQueryUrl(addr, port), 'http://1.1.1.1:80/rssh/1/query')

if __name__ == '__main__':
    unittest.main()
