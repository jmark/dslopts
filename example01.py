#!/usr/bin/env python3

import dslopts
import pathlib

mgr = dslopts.Manager()

mgr.add(name='sourcefile', desc='input file path',  type=pathlib.Path) # mandatory positional argument
mgr.add(name='sinkfile',   desc='output file path', type=pathlib.Path) # mandatory positional argument
mgr.add(name='nsamples',   desc='sampling count',   type=int, default=10) # optional positional/keyword argument

args = mgr.parse() # returns a dictionary

print(args['sourcefile'])
print(args['sinkfile'])
print(args['nsamples'] + 1)

# Following ways of calling this script are possible:
#
# ./example01.py infile outfile
# ./example01.py infile outfile 20
# ./example01.py infile outfile nsamples=20
# ./example01.py infile sinkfile=outfile nsamples=20
# ./example01.py sourcefile=infile sinkfile=outfile nsamples=20
#
# Following ways of calling this script will raise an error:
#
# ./example01.py infile
# ./example01.py infile outfile 20
# ./example01.py sourcefile=infile outfile 20
# ./example01.py infile sinkfile=outfile nsamples=20
# ./example01.py sinkfile=outfile nsamples=20
#
# The usage message can be triggered by:
# 
# ./example02.py ?
# ./example02.py help
# ./example02.py usage
