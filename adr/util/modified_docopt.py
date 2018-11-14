from docopt import DocoptExit, Option, AnyOptions, TokenStream, Dict
from docopt import parse_defaults, parse_pattern, parse_argv, extras
from docopt import formal_usage, printable_usage, sys


def docopt(doc, argv=None, help=True, version=None, options_first=False):
    if argv is None:
        argv = sys.argv[1:]
    DocoptExit.usage = printable_usage(doc)
    options = parse_defaults(doc)
    pattern = parse_pattern(formal_usage(DocoptExit.usage), options)
    argv = parse_argv(TokenStream(argv, DocoptExit), list(options), options_first)
    pattern_options = set(pattern.flat(Option))
    for ao in pattern.flat(AnyOptions):
        doc_options = parse_defaults(doc)
        ao.children = list(set(doc_options) - pattern_options)
    extras(help, version, argv, doc)
    matched, left, collected = pattern.fix().match(argv)
    if matched:
        return Dict((a.name, a.value) for a in (pattern.flat() + collected))
    DocoptExit()
