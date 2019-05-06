$fn = 300;

out_thread_h = 10.84;
out_thread_r = 10.33;
middle_h = 42.64;
middle_r = 9.1;
in_thrad_h = 10.21;
in_thread_r = 13.07;
overall_h = 65.88;
bent_middle_h = overall_h - (out_thread_h+middle_h+in_thrad_h);

rot_mid_h = 18.81;
rot_cube_h = 9.96;

module valve(){
     cylinder(r = out_thread_r, h=out_thread_h);
     translate([0,0,out_thread_h]){ //above outter thread
             translate([0,0,21.78]){//middle of the valve
                rotate([90,0,0]){
                  translate([0,0,-middle_r]){
                      cylinder(d=23.1,h=rot_mid_h);
                    translate([0,0,rot_mid_h]){
                        translate([0,0,rot_cube_h/2])cube([34,34,rot_cube_h], center=true);
                         cube([10,34,12], center = true);
                    }
                    }
              }
         }
         cylinder(r=middle_r, h=middle_h);
         translate([0,0,middle_h]){
             cylinder(r1=middle_r, r2=out_thread_r, h= bent_middle_h);
             translate([0,0,bent_middle_h])
                 cylinder(r=out_thread_r, h=out_thread_h);
         }
     }
}
translate([0,0,-out_thread_h]);
c_x = 30;
c_y = 24;
c_z = 20;
difference(){
    translate([-c_x/2,-c_y+6,0])
    cube([c_x,c_y,c_z]);
    translate([0,0,-out_thread_h])
    valve();
    
    
}