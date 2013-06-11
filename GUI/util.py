#!/usr/bin/env python
import inspect
import sys

def raiseNotDefined():
    print "Method not implemented: %s" % inspect.stack()[1][3]
    sys.exit(1)

def raiseWithMessage(Message):
    print "Method: %s. Message %s" % (inspect.stack()[1][3], Message)
    sys.exit(1)
