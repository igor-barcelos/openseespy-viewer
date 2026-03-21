import openseespy.opensees as ops

ops.model('BasicBuilder', '-ndm', 3, '-ndf', 6)

B1 = 10.0
B2 = 3.5
D = 2.0
H = 1.5

# Create nodes
#          X          Y     Z
ops.node( 1, 0.0,      0.0, 0.0)
ops.node( 2, 0.0,      0.0, 1*H)
ops.node( 3, 0.0,      0.0, 2*H)
ops.node( 4, 0.0,      0.0, 3*H)
ops.node( 5, B1,       0.0, 0.0)
ops.node( 6, B1,       0.0, 1*H)
ops.node( 7, B1,       0.0, 2*H)
ops.node( 8, B1,       0.0, 3*H)
ops.node( 9, B1+B2,    0.0, 0.0)
ops.node(10, B1+B2,    0.0, 1*H)
ops.node(11, B1+B2,    0.0, 2*H)
ops.node(12, 0.0,      D,   0.0)
ops.node(13, 0.0,      D,   1*H)
ops.node(14, 0.0,      D,   2*H)
ops.node(15, 0.0,      D,   3*H)
ops.node(16, B1,       D,   0.0)
ops.node(17, B1,       D,   1*H)
ops.node(18, B1,       D,   2*H)
ops.node(19, B1,       D,   3*H)
ops.node(20, B1+B2,    D,   0.0)
ops.node(21, B1+B2,    D,   1*H)
ops.node(22, B1+B2,    D,   2*H)

# Create elements
# Z-dir elements
ops.element('truss',  1,  1,  2)
ops.element('truss',  2,  2,  3)
ops.element('truss',  3,  3,  4)
ops.element('truss',  4,  5,  6)
ops.element('truss',  5,  6,  7)
ops.element('truss',  6,  7,  8)
ops.element('truss',  7,  9, 10)
ops.element('truss',  8, 10, 11)
ops.element('truss',  9, 12, 13)
ops.element('truss', 10, 13, 14)
ops.element('truss', 11, 14, 15)
ops.element('truss', 12, 16, 17)
ops.element('truss', 13, 17, 18)
ops.element('truss', 14, 18, 19)
ops.element('truss', 15, 20, 21)
ops.element('truss', 16, 21, 22)
# X-dir elements
ops.element('truss', 17,  2,  6)
ops.element('truss', 18,  3,  7)
ops.element('truss', 19,  4,  8)
ops.element('truss', 20,  6, 10)
ops.element('truss', 21,  7, 11)
ops.element('truss', 22, 13, 17)
ops.element('truss', 23, 14, 18)
ops.element('truss', 24, 15, 19)
ops.element('truss', 25, 17, 21)
ops.element('truss', 26, 18, 22)
# Y-dir elements
ops.element('truss', 27,  2, 13)
ops.element('truss', 28,  3, 14)
ops.element('truss', 29,  4, 15)
ops.element('truss', 30,  6, 17)
ops.element('truss', 31,  7, 18)
ops.element('truss', 32,  8, 19)
ops.element('truss', 33, 10, 21)
ops.element('truss', 34, 11, 22)
# Bracings
ops.element('truss', 35,  9, 21)
ops.element('truss', 36, 20, 10)
ops.element('truss', 37, 10, 22)
ops.element('truss', 38, 21, 11)

# Boundary conditions
ops.fix( 1, 1, 1, 1, 0, 0, 0)
ops.fix( 5, 1, 1, 1, 0, 0, 0)
ops.fix( 9, 1, 1, 1, 0, 0, 0)
ops.fix(12, 1, 1, 1, 0, 0, 0)
ops.fix(16, 1, 1, 1, 0, 0, 0)
ops.fix(20, 1, 1, 1, 0, 0, 0)

# Loads
ops.timeSeries('Linear', 1)

ops.pattern('Plain', 1, 1)
ops.load(4, 5.0, 0.0, -10.0, 0.0, 0.0, 0.0)
ops.load(8, 5.0, 0.0, -10.0, 0.0, 0.0, 0.0)
