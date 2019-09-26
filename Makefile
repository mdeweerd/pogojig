# Installation-dependent settings. You can overwrite these in a file called config.mk in the same directory as this makefile. See readme.creole.
INKSCAPE := inkscape
OPENSCAD := openscad
PYTHON := python2
ASYMPTOTE := asy

# Settings affecting the compiled results. You can overwrite these in a file called settings.mk in the same directory as this makefile. See readme.creole.
DXF_FLATNESS := 0.1

# Non-file goals.
.PHONY: all clean generated dxf stl asy pdf

# Include the configuration files.
-include config.mk settings.mk

# Command to run the Python scripts.
PYTHON_CMD := PYTHONPATH="support" $(PYTHON)
INKSCAPE_CMD := INKSCAPE=$(INKSCAPE) DXF_FLATNESS=$(DXF_FLATNESS) $(PYTHON_CMD) -m inkscape  
OPENSCAD_CMD := OPENSCAD=$(OPENSCAD) $(PYTHON_CMD) -m openscad

all: src/jig.stl src/pcb_shape.dxf

clean:
	rm -f src/input.preprocessed.dxf
	rm -f src/input.preprocessed.svg
	rm -f src/jig.stl
	rm -f src/pcb_shape.dxf

src/input.preprocessed.dxf: src/input.preprocessed.svg
	$(INKSCAPE_CMD) $< $@

src/pcb_shape.dxf: src/pcb_shape.scad src/input.preprocessed.dxf
	$(OPENSCAD_CMD) $< $@

src/jig.stl: src/jig.scad src/input.preprocessed.dxf
	$(OPENSCAD_CMD) $< $@

src/input.preprocessed.svg: input.svg
	support/inkscape_svg_filter_layers.py $< $@ --only --name "Test Points" "Mounting Holes" "Grip Slots" "Outline"

