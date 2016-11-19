#!/usr/bin/env python3

import dslopts
import pathlib

def ExistingPath(arg):
    pth = pathlib.Path(arg)
    if not pth.exists():
        raise OSError("'%s' does not exists!" % pth)
    return pth

def ConstrainedInt(arg):
    nr = int(arg)
    if 1 <= nr <= 4:
        return nr
    raise ValueError("Method number must be within 0 and 4: '%d' given!")

appendix = """  Methods are:

    1 -> method 1
    2 -> method 2 
    3 -> method 3 
    4 -> method 4 
"""

with dslopts.Manager(scope=globals(),appendix=appendix) as mgr:
    mgr.add(name='srcfile' ,desc=' input file path' ,type=ExistingPath)
    mgr.add(name='snkfile' ,desc='output file path' ,type=ExistingPath)
    mgr.add(name='method'  ,desc='method nr: 1-4'   ,type=ConstrainedInt, default=3)

print(srcfile)
print(snkfile)
print("you asked for method: %d" % method)

# Following ways of calling this script are possible:
#
# ./example02.py infile outfile
# ./example02.py infile outfile 1
# ./example02.py infile outfile method=3
# ./example02.py infile snkfile=outfile method=4
# ./example02.py infile snkfile=outfile
# ./example02.py srcfile=infile snkfile=outfile method=2
#
# Following ways of calling this script will raise an error:
#
# ./example02.py outfile
# ./example02.py infile outfile 0
# ./example02.py infile outfile method=5
# ./example02.py infile snkfile=outfile 4
# ./example02.py srcfile=infile outfile method=2
# ./example02.py srcfile=infile outfile 2
#
# The usage message can be triggered by:
# 
# ./example02.py ?
# ./example02.py help
# ./example02.py usage
