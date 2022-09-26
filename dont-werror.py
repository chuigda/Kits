#!/bin/env python3

import os, sys

process = sys.argv[0] + '-back'
args = []
for arg in sys.argv:
    if arg == '-Werror':
        print('Fuck you google, I say, fuck you! I\'d punch my fist into your fucking asshole!')
    else:
        args.append(arg)

args.append('-Wno-error')
os.execvp(process, args)
