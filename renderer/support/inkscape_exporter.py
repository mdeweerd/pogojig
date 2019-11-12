#!/usr/bin/env python3

import os
import shutil
import tempfile

from pogojig.inkscape import effect, inkscape

from xvfbwrapper import Xvfb


def _unfuck_svg_document(temp_svg_path):
    """
    Unfucks an SVG document so is can be processed by the better_dxf_export
    plugin (or what's left of it).
    """
    command_line = inkscape.InkscapeCommandLine(temp_svg_path)
    layers = command_line.layers
    
    command_line.apply_to_document('LayerUnlockAll', 'LayerShowAll')
    
    layer_copies = []
    
    for i in layers:
        layer_copy = command_line.duplicate_layer(i)
        layer_copies.append(layer_copy)
        
        command_line.apply_to_layer_content(layer_copy, 'ObjectToPath')
        command_line.apply_to_layer_content(layer_copy, 'SelectionUnGroup')
        command_line.apply_to_layer_content(layer_copy, 'EditUnlinkClone')
        
        if not i.use_paths:
            command_line.apply_to_layer_content(layer_copy, 'StrokeToPath')
            command_line.apply_to_layer_content(layer_copy, 'SelectionUnion')
    
    for original, copy in zip(layers, layer_copies):
        command_line.clear_layer(original)
        command_line.move_content(copy, original)
        command_line.delete_layer(copy)
    
    command_line.apply_to_document('FileSave', 'FileClose', 'FileQuit')
    command_line.run()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', metavar='input.svg', help='Inkscape SVG input file')
    parser.add_argument('outfile', metavar='output.dxf', help='DXF output file')
    args = parser.parse_args()

    with Xvfb():
        effect.ExportEffect.check_document_units(args.infile)

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_svg_path = os.path.join(tmpdir, os.path.basename(args.infile))
            shutil.copyfile(args.infile, temp_svg_path)

            _unfuck_svg_document(temp_svg_path)

            export_effect = effect.ExportEffect()
            export_effect.affect(args=[temp_svg_path], output=False)

        with open(args.outfile, 'w') as f:
            export_effect.write_dxf(f)

