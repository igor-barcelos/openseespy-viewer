import openseespy.opensees as ops

ops.model('BasicBuilder', '-ndm', 2, '-ndf', 3)

H = 3
B = 2*H

# Create nodes
ops.node(1, 0.0, 0.0)
ops.node(2, 0.0, 1.0)
ops.node(3, B/2, H)
ops.node(4, B, 1.0)
ops.node(5, B, 0.0)

# Create elements
ops.element('truss', 1, 1, 2)
ops.element('truss', 2, 2, 3)
ops.element('truss', 3, 3, 4)
ops.element('truss', 4, 4, 5)

# Boundary conditions
ops.fix(1, 1, 1, 1)
ops.fix(5, 1, 1, 0)
