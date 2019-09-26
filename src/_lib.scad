
module hole(l, step, w){
    translate([0, 0, -eps]) {
        union(){
            linear_extrude(l+eps*2)
                children();
            minkowski(){
                linear_extrude(eps) children();
                cylinder(step, w, 0);
            }
        }
        marker_r = 4;
        marker_w = 1;
        linear_extrude(1)
        difference() {
            offset(marker_r+0.5*marker_w) children();
            offset(marker_r-0.5*marker_w) children();
        }
    }
}

module top_chamfer(height, chamfer){
    difference(){
        linear_extrude(height) children();
        translate([0,0,height+eps])
        union() {
            for(w=[0:.2:chamfer]){
                mirror([0,0,1])
                linear_extrude(chamfer-w)
                difference(){
                    offset(1) children();
                    offset(-w) children();
                }
            }
        }
    }
}

module base_shape(wall){
    offset(grip_rounding) offset(-grip_rounding)difference(){
        hull() offset(wall)
            children();
        import(input_file, layer="Grip Slots");
    }
}

module holder(height, depth, wall, tolerance, chamfer){
    difference() {
        top_chamfer(height, chamfer/2) 
        //linear_extrude(height)
        base_shape(wall) children();
        translate([0,0,height-depth])
        linear_extrude(depth+eps) offset(tolerance)
            children();
        translate([0,0,height-chamfer+eps]) minkowski(){
            linear_extrude(eps) children();
            cylinder(chamfer, 0, chamfer);
        }
    }
}

module mounting_hole(height, inset_depth, inset_extra){
    union(){
        translate([0,0,-eps])
            linear_extrude(height+2*eps)
                children();
        translate([0,0,height-inset_depth])
            linear_extrude(inset_depth+eps)
                offset(inset_extra)
                    children();
    }
}

module jig(height, depth, wall, tolerance, chamfer) {
    difference(){
        holder(height, depth, wall, tolerance, chamfer)
            import(input_file, layer="Outline");
        hole(height-depth, 2, 1)
            import(input_file, layer="Test Points");
        mounting_hole(height, 3, 2)
            import(input_file, layer="Mounting Holes");
    }
}
