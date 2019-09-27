# Environment variables:
# INKSCAPE_DXF_FLATNESS controls inkscape SVG->DXF export curve flatness (default: 0.1)
# INKSCAPE, OPENSCAD: Commands to use for inkscape and openscad

OPENSCAD ?= openscad

all: out.zip
	
out.zip: out/jig.stl out/pcb_shape.dxf out/kicad
	zip -r out.zip out

src/input.preprocessed.dxf: src/input.preprocessed.svg
	support/inkscape_exporter.py $< $@

out/pcb_shape.dxf: src/pcb_shape.scad src/input.preprocessed.dxf out
	$(OPENSCAD) -o $@ $<

out/jig.stl: src/jig.scad src/input.preprocessed.dxf
	$(OPENSCAD) -o $@ $<

out/kicad: input.svg out/pcb_shape.dxf
	support/generate_kicad.py $^ $@

src/input.preprocessed.svg: input.svg
	support/inkscape_svg_filter_layers.py $< $@ --only --name "Test Points" "Mounting Holes" "Grip Slots" "Outline"

out:
	mkdir -p out

.PHONY: clean
clean:
	rm -f src/input.preprocessed.dxf
	rm -f src/input.preprocessed.svg
	rm -rf out

