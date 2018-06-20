#!/usr/bin/env python3

import mdl
import sys

from argparse import ArgumentParser

from display import *
from matrix import *
from draw import *

num_frames = int(1)
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
to some default value, and print(out a message)
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

    num_frames = int(num_frames)
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
                value += delta

def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        'mdl_file',
        type=str
    )
    return parser.parse_args()

def main():
    view = [0,
        0,
        1]
    ambient = [100,
               100,
               100]
    light = [  ]
    endlight = []
    usedplus2 = []
    dendlight = []
    areflect = [0.1,
                0.1,
                0.1]
    dreflect = [0.5,
                0.5,
                0.5]
    sreflect = [0.5,
                0.5,
                0.5]
    glowy = True
    color = [0, 0, 0]
    linecolor = [255, 150, 80]
    tmp = new_matrix()
    ident( tmp )

    stack = [ [x[:] for x in tmp] ]
    screen = new_screen()
    zbuffer = new_zbuffer()
    tmp = []
    step_3d = 20
    consts = ''
    coords = []
    coords1 = []

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

    for command in commands:
        c = command['op']
        if c == 'light' and not(command['light'] in usedplus2):
            light.append([symbols[command['light']][1]['color'], symbols[command['light']][1]['location']])
            if (command['light'] + '2') in symbols:
                usedplus2.append(command['light']+'2')
                endlight.append([symbols[command['light']+'2'][1]['color'], symbols[command['light']+'2'][1]['location']])
                del symbols[command['light']+'2']
            else:
                endlight.append([])


    if num_frames>1:
        a = 0
        while a < len(light):
            if endlight[a] == []:
                 dendlight.append([[0, 0, 0], [0, 0, 0]])
            else:
                d0 = (endlight[a][0][0] - light[a][0][0])/num_frames
                d1 = (endlight[a][0][1] - light[a][0][1])/num_frames
                d2 = (endlight[a][0][2] - light[a][0][2])/num_frames
                d3 = (endlight[a][1][0] - light[a][1][0])/num_frames
                d4 = (endlight[a][1][1] - light[a][1][1])/num_frames
                d5 = (endlight[a][1][2] - light[a][1][2])/num_frames
                dendlight.append([[d0, d1, d2], [d3, d4, d5]])
            a += 1
    print(light)
    print(endlight)
    print(dendlight)
    q = 0
    while q < num_frames:
        if num_frames>1:
            a = 0
            while a < len(light):
                light[a][0][0] += dendlight[a][0][0]
                light[a][0][1] += dendlight[a][0][1]
                light[a][0][2] += dendlight[a][0][2]
                light[a][1][0] += dendlight[a][1][0]
                light[a][1][1] += dendlight[a][1][1]
                light[a][1][2] += dendlight[a][1][2]
                a += 1
        print(commands)
        for command in commands:
            c = command['op']
            args = command['args']
            if not args == None:
                args = command['args'][:]

            for knob in knobs[q]:
                symbols[knob][1] = knobs[q][knob]

                if (c=='move' and command['knob'] != None):
                    args[0] *= symbols[knob][1]
                    args[1] *= symbols[knob][1]
                    args[2] *= symbols[knob][1]
                elif (c=='rotate' and command['knob'] != None):	
                    args[1] *= symbols[knob][1]
                elif (c=='scale' and command['knob'] != None):
                    args[0] *= symbols[knob][1]
                    args[1] *= symbols[knob][1]
                    args[2] *= symbols[knob][1]


            if c == 'box':
                if isinstance(args[0], str):
                    consts = args[0]
                    args = args[1:]
                if isinstance(args[-1], str):
                    coords = args[-1]
                add_box(tmp,
                    args[0], args[1], args[2],
                    args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, areflect, dreflect, sreflect)
                tmp = []
            elif c == 'sphere':
                add_sphere(tmp,
                       args[0], args[1], args[2], args[3], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, areflect, dreflect, sreflect)
                tmp = []
            elif c == 'torus':
                add_torus(tmp,
                      args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, areflect, dreflect, sreflect)
                tmp = []
            elif c == 'line':
                if isinstance(args[0], str):
                    consts = args[0]
                    args = args[1:]
                if isinstance(args[3], str):
                    coords = args[3]
                    args = args[:3] + args[4:]
                if isinstance(args[-1], str):
                    coords1 = args[-1]
                f = 5
                dr = linecolor[0]/f
                dg = linecolor[1]/f
                db = linecolor[2]/f
                g = [0, 0, 0]
                while f >= 0:
                    add_edge(tmp,
                         args[0], args[1]+f, args[2], args[3], args[4]-f, args[5])
                    add_edge(tmp,
                         args[0], args[1]-f, args[2], args[3], args[4]-f, args[5])
                    add_edge(tmp,
                         args[0]+f, args[1], args[2], args[3]+f, args[4], args[5])
                    add_edge(tmp,
                         args[0]-f, args[1], args[2], args[3]-f, args[4], args[5])
                    matrix_mult( stack[-1], tmp )
                    draw_lines(tmp, screen, zbuffer, g)
                    tmp = []
                    g = [g[0]+dr, g[1]+dg, g[2]+db]
                    f -= 1

            elif c == 'move':
                tmp = make_translate(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []

            elif c == 'mesh':
                '''filename = command['cs']
                f = open(filename+'.obj', 'r')
                t = f.readlines()
                vertices = [[0,0,0]]
                faces = []
                for y in t:
                    r = y.split()
                    if r[0] == 'v':
                        r.remove('v')
                        r = [int(r[0]), int(r[1]), int(r[2])]
                        vertices.append(r)
                    elif r[0] == 'f':
                        r.remove('f')
                        r = [int(r[0]), int(r[1]), int(r[2])]
                        faces.append(r)
                for face in faces:
                    y = 0
                    while y < len(face):
                        if command['constants']=='glowy':
                            f = 5
                            dr = linecolor[0]/f
                            dg = linecolor[1]/f
                            db = linecolor[2]/f
                            g = [0, 0, 0]
                            while f >= 0:
                                add_edge(tmp,
                         vertices[face[y]][0], vertices[face[y]][1]+f, vertices[face[y]][2], vertices[face[(y+1)%len(face)]][0],  
vertices[face[(y+1)%len(face)]][1]-f, 
vertices[face[(y+1)%len(face)]][2]
)
                                add_edge(tmp,
                         vertices[face[y]][0], vertices[face[y]][1]-f, vertices[face[y]][2], vertices[face[(y+1)%len(face)]][0],  vertices[face[(y+1)%len(face)]][1]-f, vertices[face[(y+1)%len(face)]][2])
                                add_edge(tmp,
                         vertices[face[y]][0]+f, vertices[face[y]][1], vertices[face[y]][2], vertices[face[(y+1)%len(face)]][0]+f,  vertices[face[(y+1)%len(face)]][1], vertices[face[(y+1)%len(face)]][2])
                                add_edge(tmp,
                         vertices[face[y]][0]-f, vertices[face[y]][1], vertices[face[y]][2], vertices[face[(y+1)%len(face)]][0]-f,  vertices[face[(y+1)%len(face)]][1], vertices[face[(y+1)%len(face)]][2])
                                matrix_mult( stack[-1], tmp )
                                draw_lines(tmp, screen, zbuffer, g)
                                tmp = []
                                g = [g[0]+dr, g[1]+dg, g[2]+db]
                                f -= 1
                        else:
                            add_edge(tmp,
                     vertices[face[y]][0], vertices[face[y]][1], vertices[face[y]][2], vertices[face[(y+1)%len(face)]][0], vertices[face[(y+1)%len(face)]][1], vertices[face[(y+1)%len(face)]][2])
                            matrix_mult( stack[-1], tmp )
                            draw_lines(tmp, screen, zbuffer, [255, 255, 255])
                            tmp = []
                        y += 1'''
                pass





            elif c == 'scale':
                tmp = make_scale(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                theta = args[1] * (math.pi/180)
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'ambient':
                ambient = [args[0], args[1], args[2]]
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
            elif c == 'constants':
                areflect[0] = symbols[command['constants']][1]['red'][0]
                areflect[1] = symbols[command['constants']][1]['green'][0]
                areflect[2] = symbols[command['constants']][1]['blue'][0]
                dreflect[0] = symbols[command['constants']][1]['red'][1]
                dreflect[1] = symbols[command['constants']][1]['green'][1]
                dreflect[2] = symbols[command['constants']][1]['blue'][1]
                sreflect[0] = symbols[command['constants']][1]['red'][2]
                sreflect[1] = symbols[command['constants']][1]['green'][2]
                sreflect[2] = symbols[command['constants']][1]['blue'][2]


        if vary==True:
            save_extension(screen,'./anim/'+ basename+('%03d' % q) + '.png')
        tmp = new_matrix()
        ident( tmp )

        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
        step_3d = 20
        q += 1
    if vary==True:
        make_animation(basename)

if __name__ == '__main__':
    main()