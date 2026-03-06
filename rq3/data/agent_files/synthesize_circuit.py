import stim

# Load stabilizers
with open('my_task_stabilizers.txt', 'r') as f:
    stabilizers = [stim.PauliString(line.strip()) for line in f if line.strip()]

print(f"Loaded {len(stabilizers)} stabilizers.")

# Create Tableau
# Note: from_stabilizers expects a list of stabilizers.
# If underconstrained, we must set allow_underconstrained=True.
try:
    tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
    print("Tableau created successfully.")
    
    # Synthesize using different methods
    methods = ["gaussian", "cz_series", "riemannian"] # method names might vary in stim versions, usually "elimination" is default?
    # stim.Tableau.to_circuit(method=...)
    # Check help or try default.
    
    # Try default (Gaussian elimination)
    circ_default = tableau.to_circuit("elimination")
    
    # Count CX
    cx_default = 0
    for op in circ_default:
        if op.name == "CX" or op.name == "CNOT":
            cx_default += len(op.targets_copy()) // 2
    
    print(f"Default synthesis: {cx_default} CX gates.")
    
    # Try graph state synthesis
    try:
        circ_graph = tableau.to_circuit("graph_state")
        cx_graph = 0
        for op in circ_graph:
            if op.name == "CX" or op.name == "CNOT":
                cx_graph += len(op.targets_copy()) // 2
        print(f"Graph state synthesis: {cx_graph} CX gates.")
        
        with open('candidate_graph.stim', 'w') as f:
            f.write(str(circ_graph))
    except Exception as e:
        print(f"Graph state synthesis failed: {e}")

    with open('candidate_elimination.stim', 'w') as f:
        f.write(str(circ_default))
        
except Exception as e:
    print(f"Synthesis failed: {e}")
