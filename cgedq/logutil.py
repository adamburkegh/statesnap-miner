#
# Python logging package mangles unicode sent to the git bash console on 
# windows, even on later versions. 
#
# This is despite fixes like:
# https://bugs.python.org/issue37111
#
# Symptom: logger.info(hanzi) will output the literal \u597d for hao3
#
# This module is a workaround. It is quite hard to get at the root logger 
# itself, so we somewhat brutally redefine the main logging methods to point
# to a logger that respects levels, but otherwise just prints to console.
# 
# Sets log level to INFO. To reset, call setLogLevel()
#

import logging
import sys


''' 
Shortcut all the normal handling after the log level checks, and just
print with whatever formatting it came in with.
'''
class PrintLogger(logging.Logger):
    def __init__(self,name):
        super().__init__(name)

    def _log(self, level, msg, args, exc_info=None, extra=None, 
            stack_info=False, stacklevel=1):
        print(msg)

root = logging.getLogger()

plog = PrintLogger('')
plog.setLevel(logging.INFO)
# plog.setLevel(logging.WARN)


debug   = plog.debug
info    = plog.info
warning = plog.warning
error   = plog.error

logging.debug = debug
logging.info = info
logging.warning = warning
logging.error = error

denc = 'utf-8'

def configencoding():
    sys.stdout.reconfigure(encoding=denc)   

configencoding()

def setLogLevel(level):
    root.setLevel(level)
    plog.setLevel(level)


