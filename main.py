#!/usr/bin/env python3

import mdl
import sys

from argparse import ArgumentParser
from pprint import pprint

def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        'mdl_file',
        type=str
    )
    return parser.parse_args()

def main():
    args = parse_args()
    with open(args.mdl_file, 'r', encoding='utf-8') as mdl_file:
        mdl_script = mdl_file.read()
    result = mdl.parse(mdl_script)
    if not result:
        print("Parsing failed.", file=sys.stderr)
        sys.exit(1)
    commands, symbols = result
    pprint(commands)
    pprint(symbols)

if __name__ == '__main__':
    main()