include <_settings.scad>
include <_lib.scad>

difference(){
    base_shape(wall+pcb_extra)
        import(input_file, layer="Outline");
    import(input_file, layer="Mounting Holes");
}