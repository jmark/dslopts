#!/usr/bin/env python3

# -----------------------------------------------------------------------------
# MIT License
# 
# Copyright (c) 2016 Johannes Markert <me@jmark.de> http://www.jmark.de
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----------------------------------------------------------------------------
# In addition to the license above:
#
# BEER-WARE License
# 
# Johannes Markert <me@jmark.de> is the author of this project. As long as you
# retain this notice you can do whatever you want with this stuff. If we meet
# some day, and you think this stuff is worth it, you can buy me a beer in
# return.
# -----------------------------------------------------------------------------

'''
Damn Small Commandline Arguments/Options Parse and Retrieval Agent

This is a KISS python module for parsing commandline arguments without defining
any switches. One can use keywords, set default values in the same way as it is
done for Python function prototypes. Additionally a convenient way of
constraining input data and enforcing types is provided. It builds a nice
formmatted usage page automatically.

For a working example execute this module directly or refer to the accompanied
examples.

* conventional:
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


* with context manager:
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
'''

import sys

class Manager:
    def __init__(self, argsdict=None, scope=None, appendix=''):
        """
            argsdict    -> fill given dictionary with parsed parameters
            scope       -> install arguments as variables in given scope
            appendix    -> add appendix to the end of the usage message
        """
        self.argn = list() # argument position
        self.proc = dict() # argument processing routines

        self.args      = {'_progname_': sys.argv[0]}
        self.helpkws   = 'help usage what how ?'.split()
        self.argsdict  = argsdict
        self.scope     = scope
        self.appendix  = appendix
        self.add.__func__.kword = False
        self.parse.__func__.kword = False

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if isinstance(value,Exception):
            raise
        self.parse()
        if self.argsdict:
            self.argsdict.update(self.args)
        if self.scope:
            self.install_into_scope(self.scope)

    def add(self, name, desc='--', type=str, default=None):
        if self.add.__func__.kword is True and default is None:
            raise SyntaxError("Non-default argument '%s' follows default argument at %d." % (name, len(self.argn)))
        if default is not None:
            self.add.__func__.kword = True

        self.argn.append(name)
        self.args[name] = default
        self.proc[name] = {
            'name':     name,
            'desc':     desc,
            'type':     type,
            'default':  default,
        }

    def parse(self, ARGV=None):
        if ARGV is None: ARGV = sys.argv[1:]

        # shortcuts
        argn = self.argn
        proc = self.proc
        args = self.args
        func = self.parse.__func__

        argv = []; ignv = []; ispos = True
        for i, arg in enumerate(ARGV):
            # detect ignored arguments
            if arg == '--':
                ignv = ARGV[i+1:]
                break

            # scan for help/usage arguments
            if arg.lower() in self.helpkws:
                self.print_usage()
                sys.exit(1)

            # parse given argument
            kv = arg.split('=',1)
            if len(kv) == 1:
                name, value = argn[i], arg
                if func.kword:
                    raise SyntaxError("Positional argument %d follows keyword argument." % (i+1))
            elif len(kv) == 2:
                name, value = kv
                func.kword = True

            # type checking
            args[name] = proc[name]['type'](value)

        # check if all defined arguments are set
        for i,name in enumerate(argn,1):
            if args[name] is None:
                raise TypeError("Missing required positional argument: '%s' at %d." % (name, i))

        args['_ignored_'] = ignv
        return args

    def install_into_scope(self, scope):
        scope.update(self.args)

    def usage(self):
        # shortcuts
        proc   = self.proc
        args   = self.args
        argn   = self.argn

        hdName = 'name'
        hdType = 'type'
        hdDeft = 'default value'
        hdDesc = 'description'

        lnName = max([len(hdName)]+[len(proc[x]['name']) for x in argn])
        lnType = max([len(hdType)]+[len(proc[x]['type'].__name__) for x in argn])
        lnDeft = max([len(hdDeft)]+[len(str(proc[x]['default'])) for x in argn])
        lnDesc = max([len(hdDesc)]+[len(proc[x]['desc']) for x in argn])

        primer = "usage: %s arg0 arg1 ... opt0=value0 opt1=value1 ... -- ... (ignored args)\n\n" % args['_progname_']
        primer += "  * Either '%s' triggers this help message." % "', '".join(self.helpkws)
        primer += " For more\n    information try: 'pydoc dslopts'.\n"
        primer += "\n"

        header = "       | %-*s  | %-*s  | %-*s  | %-*s\n" % \
                    (lnName, hdName, lnType, hdType, lnDeft, hdDeft, lnDesc, hdDesc)
        stroke = '  ' + '-' * (len(header)-2) + "\n"

        table  = header + stroke 
        for i, arg in enumerate((proc[x] for x in argn),1):
            table += "  %3d  | %-*s  | %-*s  | %-*s  | %-*s\n" % (
                i, lnName, arg['name'], lnType, arg['type'].__name__, lnDeft, str(arg['default']), lnDesc, arg['desc'])
        if self.appendix: table += "\n"

        return primer + table + self.appendix

    def print_usage(self):
        print(self.usage(), file=sys.stderr)

if __name__ == '__main__':
    import pathlib

    def ExistingPath(arg):
        pth = pathlib.Path(arg)
        if not pth.exists():
            raise OSError("'%s' does not exists!" % pth)
        return pth

    def PositiveInt(arg):
        x = int(arg)
        if x > 0:
            return x
        raise ValueError("'%d' must be positive!" % x)

    with Manager(scope=locals()) as mgr:
        mgr.add(name='arg0', desc='argument 0', type=ExistingPath)
        mgr.add(name='arg1', desc='argument 1', type=PositiveInt)
        mgr.add(name='arg2', desc='argument 2', default='some default value')

    print(arg0)
    print(arg1)
