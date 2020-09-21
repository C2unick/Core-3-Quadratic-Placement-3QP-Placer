# Core-3-Quadratic-Placement-3QP-Placer
executing 3 Quadratic Placement (QP) matrix solves. One solve on the full-size netlist, and then executing one vertical cut, to assign half of the gates to each side of this cut, then one containment step on each side of that cut, then finally, executing the other two solves , one solve on each side.
# the files:
-3QP.py is the proram 
-the other files are some netlists with different sizes 
# the description of the input as the following:
-First line: two integers.The number of gates G and number of nets N
-Next G lines: one line per gate. Each line has a GateI D number(starting from 1 and continuing in order without any gaps to gate #G),then the number M of nets connected to this gate,then the Net IDs of the M nets this gate is connected to.
-Nextline: Number of pads P on this chip.
-Next P lines: one line per pad. Each line has a Pad ID(starting at 1,and continuing in order without any gaps to pad #P),then the NetID this pad is connected to,then an Xcoordinate and a Ycoordinate.
