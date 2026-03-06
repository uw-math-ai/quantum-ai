import stim
import sys
import json
import os

def run_solve():
    filename = r'data\gemini-3-pro-preview\agent_files\stabilizers_119.txt'
    if not os.path.exists(filename):
        print(f"File {filename} not found.")
        sys.exit(1)
        
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    fixed_stabilizers = []
    
    for i, line in enumerate(lines):
        if len(line) == 121:
            # Fix index 95 (python index 95, line 96)
            # The erroneous line:
            # II...II (71 Is) + ZIIZIIIIIZIIZ + II...II (37 Is) = 121
            # We want start 69.
            # 69 + 13 + 37 = 119
            new_line = 'I'*69 + 'ZIIZIIIIIZIIZ' + 'I'*37
            if len(new_line) != 119:
                print(f"Error fixing line {i}: length {len(new_line)}")
                sys.exit(1)
            fixed_stabilizers.append(new_line)
        else:
            fixed_stabilizers.append(line)
            
    # Check length
    for s in fixed_stabilizers:
        if len(s) != 119:
            print(f"Length mismatch: {len(s)}")
            sys.exit(1)
            
    print(f"Loaded {len(fixed_stabilizers)} stabilizers.")
    
    try:
        paulis = [stim.PauliString(s) for s in fixed_stabilizers]
        
        # We need to specify allow_underconstrained=True because we have 118 stabilizers for 119 qubits
        # This will set the logical qubit to +Z or +X or something arbitrary.
        tableau = stim.Tableau.from_stabilizers(paulis, allow_underconstrained=True, allow_redundant=True)
        
        circuit = tableau.to_circuit()
        print(f"Generated circuit with {len(circuit)} instructions.")
        
        # Save the stabilizers to 'stabilizers_119_fixed.txt' so I can read it in the next step.
        fixed_path = r'data\gemini-3-pro-preview\agent_files\stabilizers_119_fixed.txt'
        with open(fixed_path, 'w') as f:
            for s in fixed_stabilizers:
                f.write(s + '\n')
                
        # Also save the circuit
        circuit_path = r'data\gemini-3-pro-preview\agent_files\circuit_119_fixed.stim'
        with open(circuit_path, 'w') as f:
            f.write(str(circuit))
            
        print(f"Success. Saved to {fixed_path} and {circuit_path}")
        
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    run_solve()
