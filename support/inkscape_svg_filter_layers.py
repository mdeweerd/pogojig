#!/usr/bin/env python3

import xml.etree.ElementTree as xe
import argparse
import re


if __name__ != '__main__':
    raise SystemError('Not running as shell script')


parser = argparse.ArgumentParser()
parser.add_argument('infile', metavar='input.svg', type=argparse.FileType('r'))
parser.add_argument('outfile', metavar='output.svg', type=argparse.FileType('wb'))
parser.add_argument('-n', '--name', nargs='+', default=[], help='Remove layers with this exact name (case-insensitive)')
parser.add_argument('-r', '--regex', nargs='+', default=[], help='Remove layers with names matching this regex')
parser.add_argument('-i', '--invisible', action='store_true', help='Remove hidden (invisible) layers')
parser.add_argument('-o', '--only', action='store_true', help='Invert logic, i.e. keep matched layers and discard others')
parser.add_argument('-d', '--strip-defs', action='store_true', help='Also strip any <defs> tags (off by default)')
args = parser.parse_args()

doc = xe.fromstring(args.infile.read())
ns = {
        'svg': 'http://www.w3.org/2000/svg',
        'inkscape': 'http://www.inkscape.org/namespaces/inkscape',
        'sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd'
}

if args.strip_defs:
    for elem in doc.findall('svg:defs', ns):
        doc.remove(elem)

for i, g in enumerate(doc.findall('svg:g', ns)):
    if g.attrib.get(f'{{{ns["inkscape"]}}}groupmode') != 'layer':
        continue

    label = g.attrib.get(f'{{{ns["inkscape"]}}}label', '')
    match = (
            any(label == name for name in args.name) or
            any(re.match(regex, label) for regex in args.regex) or
            ('display:none' in g.attrib.get('style', '') and args.hidden)
            )
    print(f'Layer {i} "{label}": {"match" if match else "not found"}', end='')

    if match != args.only:
        print(', removing.')
        doc.remove(g)
    else:
        print()

args.outfile.write(xe.tostring(doc))
