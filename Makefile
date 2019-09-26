# Environment variables:
# INKSCAPE_DXF_FLATNESS controls inkscape SVG->DXF export curve flatness (default: 0.1)
# INKSCAPE, OPENSCAD: Commands to use for inkscape and openscad

OPENSCAD ?= openscad

all: src/jig.stl src/pcb_shape.dxf

src/input.preprocessed.dxf: src/input.preprocessed.svg
	support/inkscape_exporter.py $< $@

src/pcb_shape.dxf: src/pcb_shape.scad src/input.preprocessed.dxf
	$(OPENSCAD) -o $@ $<

src/jig.stl: src/jig.scad src/input.preprocessed.dxf
	$(OPENSCAD) -o $@ $<

src/input.preprocessed.svg: input.svg
	support/inkscape_svg_filter_layers.py $< $@ --only --name "Test Points" "Mounting Holes" "Grip Slots" "Outline"

.PHONY: clean
clean:
	rm -f src/input.preprocessed.dxf
	rm -f src/input.preprocessed.svg
	rm -f src/jig.stl
	rm -f src/pcb_shape.dxf

