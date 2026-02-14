import stim
import sys

def parse_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

stabilizers_str = parse_stabilizers('stabilizers_75.txt')
print(f"Loaded {len(stabilizers_str)} stabilizers.")

stabilizers = [stim.PauliString(s) for s in stabilizers_str]

try:
    # Attempt to create tableau from stabilizers
    # allow_underconstrained=True because we have 74 stabilizers for 75 qubits
    # allow_redundant=True just in case
    t = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
    print("Successfully created Tableau from stabilizers.")
    
    # Generate circuit
    # The tableau T maps Z_k -> stabilizer[k].
    # So T applied to |0> (stabilized by Z_k) produces state stabilized by stabilizer[k].
    c = t.to_circuit("recompiled") 
    # "recompiled" might produce better circuits? default is usually fine.
    # Actually just to_circuit() is standard.
    
    # Let's check the method signature of to_circuit
    # help(stim.Tableau.to_circuit)
    c = t.to_circuit(method="elimination") # or "graph_state" if available? 
    # Actually just default is fine.
    
    print("Circuit generated.")
    
    # We need to ensure we initialize to |0> first? 
    # The circuit returned by to_circuit implements the unitary U.
    # So we should prepend R (Reset) or just assume start at |0>.
    # The problem says "starting from |0⟩^{⊗ 75}".
    # So we don't strictly need explicit reset if we assume clean initialization, 
    # but adding R operations at the beginning is safe.
    
    # Create a full circuit with initialization
    full_circuit = stim.Circuit()
    # Add resets
    full_circuit.append("R", range(75))
    # Append the tableau circuit
    full_circuit += c
    
    with open('circuit_75.stim', 'w') as f:
        f.write(str(full_circuit))
        
except Exception as e:
    print(f"Error creating tableau/circuit: {e}")
    import traceback
    traceback.print_exc()
