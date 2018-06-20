#!/usr/bin/env python3

import mdl
import sys

from argparse import ArgumentParser
from pprint import pprint

num_frames = 1
basename = "faraday"
vary = False
knobs = []

"""
Checks the commands array for any animation commands
(frames, basename, vary)
Should set num_frames and basename if the frames
or basename commands are present
If vary is found, but frames is not, the entire
program should exit.
If frames is found, but basename is not, set name
to some default value, and print out a message
with the name being used.
"""
def first_pass(commands):
    global num_frames
    global vary
    global basename

    for command in commands:
        op = command['op']
        args = command['args']

        if op == 'frames':
            num_frames = args[0]
        elif op == 'basename':
            basename = args[0]
        elif op == 'vary':
            vary = True

    for _ in range(num_frames):
        knobs.append({})
                
    if vary and num_frames == 1:
        print("'vary' was specified, but no frames", file=sys.stderr)
        sys.exit(1)
    elif num_frames != 1 and basename == 'faraday':
        print("No basename specified, setting to 'faraday'", file=sys.stderr)
        sys.exit(1)

"""
In order to set the knobs for animation, we need to keep
a seaprate value for each knob for each frame. We can do
this by using an array of dictionaries. Each array index
will correspond to a frame (eg. knobs[0] would be the first
frame, knobs[2] would be the 3rd frame and so on).
Each index should contain a dictionary of knob values, each
key will be a knob name, and each value will be the knob's
value for that frame.
Go through the command array, and when you find vary, go
from knobs[0] to knobs[frames-1] and add (or modify) the
dictionary corresponding to the given knob with the
appropirate value.
"""
def second_pass(commands, numf):
    global num_frames
    global knobs

    for command in commands:
        op = command['op']
        args = command['args']
        if op == 'vary':
            key = command['knob']
            startf = args[0]
            endf = args[1]
            startnum = args[2]
            endnum = args[3]

            delta = (endnum - startnum) / (endf - startf)
            value = startnum
            frame = startf

            while frame < endf:
                knobs[int(frame)].update({key: value})
                frame += 1
                value += d

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
    
    first_pass(commands)
    second_pass(commands, num_frames)

if __name__ == '__main__':
    main()