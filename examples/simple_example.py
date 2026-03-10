import openseespy.opensees as ops

# Initialize the model
ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3)

# Define materials
ops.uniaxialMaterial('Elastic', 1, 30000)  # Steel material

# Create nodes for 3-story building
# Ground level nodes
ops.node(1, 0.0, 0.0)      # Left base
ops.node(2, 10.0, 0.0)     # Right base

# First floor nodes
ops.node(3, 0.0, 12.0)     # Left column, floor 1
ops.node(4, 10.0, 12.0)    # Right column, floor 1

# Second floor nodes
ops.node(5, 0.0, 24.0)     # Left column, floor 2
ops.node(6, 10.0, 24.0)    # Right column, floor 2

# Third floor nodes
ops.node(7, 0.0, 36.0)     # Left column, floor 3
ops.node(8, 10.0, 36.0)    # Right column, floor 3

# Fix base nodes
ops.fix(1, 1, 1, 1)  # Fix all DOFs
ops.fix(2, 1, 1, 1)

# Define elements (columns and beams)
# Cross-sectional area for columns and beams
A_col = 50.0  # Column area
A_beam = 40.0  # Beam area
A_brace = 15.0  # Bracing area

# First story columns
ops.element('Truss', 1, 1, 3, A_col, 1)  # Left column, story 1
ops.element('Truss', 2, 2, 4, A_col, 1)  # Right column, story 1

# First floor beam
ops.element('Truss', 3, 3, 4, A_beam, 1)

# Second story columns
ops.element('Truss', 4, 3, 5, A_col, 1)  # Left column, story 2
ops.element('Truss', 5, 4, 6, A_col, 1)  # Right column, story 2

# Second floor beam
ops.element('Truss', 6, 5, 6, A_beam, 1)

# Third story columns
ops.element('Truss', 7, 5, 7, A_col, 1)  # Left column, story 3
ops.element('Truss', 8, 6, 8, A_col, 1)  # Right column, story 3

# Third floor beam
ops.element('Truss', 9, 7, 8, A_beam, 1)

# Diagonal bracing (X-bracing pattern for lateral stability)
# Story 1 braces
ops.element('Truss', 10, 1, 4, A_brace, 1)  # Diagonal from base left to floor 1 right
ops.element('Truss', 11, 2, 3, A_brace, 1)  # Diagonal from base right to floor 1 left

# Story 2 braces
ops.element('Truss', 12, 3, 6, A_brace, 1)  # Diagonal from floor 1 left to floor 2 right
ops.element('Truss', 13, 4, 5, A_brace, 1)  # Diagonal from floor 1 right to floor 2 left

# Story 3 braces
ops.element('Truss', 14, 5, 8, A_brace, 1)  # Diagonal from floor 2 left to floor 3 right
ops.element('Truss', 15, 6, 7, A_brace, 1)  # Diagonal from floor 2 right to floor 3 left

# Define loads
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

# Apply gravity loads at floor nodes (in kips)
ops.load(3, 0.0, -100.0, 0.0)  # Floor 1 load
ops.load(5, 0.0, -100.0, 0.0)  # Floor 2 load
ops.load(7, 0.0, -100.0, 0.0)  # Floor 3 load

# Run gravity analysis
ops.system('BandGeneral')
ops.numberer('Plain')
ops.constraints('Plain')
ops.integrator('LoadControl', 1.0)
ops.algorithm('Newton')
ops.analysis('Static')
ops.analyze(1)

print("Model created successfully!")
print("Nodes: 1-8 (2 base nodes + 2 nodes per floor)")
print("Elements: 15 (columns + beams + diagonal X-bracing)")
print("Applied gravity loads at floors 1, 2, and 3")
