#!/usr/bin/env python
import sys
import os
import optparse

from glue.qt.glue_application import GlueApplication


def parse(argv):
    """ Parse argument list, check validity

    :param argv: Arguments passed to program

    *Returns*
    A tuple of options, position arguments
    """
    usage = "usage: %prog [options] [FILE]"
    parser = optparse.OptionParser(usage=usage)

    parser.add_option('-x', '--execute', action='store_true', dest='script',
                      help="Execute FILE as a python script", default=False)
    parser.add_option('-g', action='store_true', dest='restore',
                      help="Restore glue session from FILE", default=False)
    parser.add_option('-c', '--config', type='string', dest='config',
                      metavar='CONFIG',
                      help='use CONFIG as configuration file')
    err_msg = verify(parser, argv)
    if err_msg:
        sys.stderr.write('\n%s\n' % err_msg)
        parser.print_help()
        sys.exit(1)

    return parser.parse_args(argv)


def verify(parser, argv):
    """ Check for input errors

    :param parser: OptionParser instance
    :param argv: Argument list
    :type argv: List of strings

    *Returns*
    An error message, or None
    """
    opts, args = parser.parse_args(argv)
    err_msg = None

    if len(args) > 1:
        err_msg = "Too many arguments"
    elif opts.script and len(args) != 1:
        err_msg = "Must provide a script\n"
    elif opts.restore and len(args) != 1:
        err_msg = "Must provide a .glu file\n"
    elif opts.config is not None and not os.path.exists(opts.config):
        err_msg = "Could not find configuration file: %s" % opts.config

    return err_msg


def start_glue(gluefile=None, config=None):
    from pickle import Unpickler

    if gluefile is not None:
        with open(gluefile) as f:
            try:
                state = Unpickler(f).load()
            except:
                QMessageBox.critical(None, "Error",
                                     "Error opening Glue file: %s" % e)
                sys.exit(1)
        data, hub = state
    else:
        data, hub = None, None

    if config is not None:
        import glue
        glue.env = glue.config.load_configuration(search_path=[config])
    ga = GlueApplication(data_collection=data, hub=hub)
    sys.exit(ga.exec_())


def execute_script(script):
    """ Run a python script and exit.

    Provides a way for people with pre-installed binaries to use
    the glue library
    """
    execfile(script)
    sys.exit(0)


def main():
    opt, args = parse(sys.argv[1:])
    if opt.restore:
        start_glue(args[0], config=opt.config)
    elif opt.script:
        execute_script(args[0])
    else:
        has_file = len(args) == 1
        has_py = has_file and args[0].endswith('.py')
        has_glu = has_file and args[0].endswith('.glu')
        if has_py:
            execute_script(args[0])
        elif has_glu:
            start_glue(args[0], config=opt.config)
        else:
            start_glue(config=opt.config)

if __name__ == "__main__":
    main()