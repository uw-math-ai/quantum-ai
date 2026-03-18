import stim
import sys
import os

def solve():
    # Load stabilizers
    stabilizers = []
    with open('target_stabilizers_challenge.txt', 'r') as f:
        # File has one stabilizer per line
        # Truncate to 92 chars to avoid issues with extra spaces/chars
        stabilizers = [line.strip()[:92] for line in f if line.strip()]

    print(f"Loaded {len(stabilizers)} stabilizers.")

    # Create Tableau
    try:
        # Convert strings to stim.PauliString
        pauli_stabilizers = [stim.PauliString(s) for s in stabilizers]
        
        # Check consistency by removing known bad stabilizer 16
        # Baseline preserves 89/90, failing 16. 16 anticommutes with 44.
        # We trust baseline's choice.
        if len(pauli_stabilizers) > 16:
            print("Removing stabilizer 16 (inconsistent with 44 and baseline).")
            del pauli_stabilizers[16]
            
        # Use allow_underconstrained=True because 89 stabilizers < 92 qubits
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True)
        print("Tableau created successfully with 89 stabilizers.")
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Synthesize circuit using graph state method
    # This method naturally produces H, S, CZ, and single qubit gates.
    # It does NOT use CX by default unless converted.
    circuit = tableau.to_circuit(method='graph_state')
    
    # Process instructions
    # Remove R/RX/RY assuming input |0>
    # Translate RX -> H (reset |0> to |+>)
    # Translate RY -> H, S (reset |0> to |i>)
    # Translate R/RZ -> Identity (reset |0> to |0>)
    
    new_circuit = stim.Circuit()
    for instruction in circuit:
        name = instruction.name
        targets = instruction.targets_copy()
        
        if name == 'R' or name == 'RZ':
            # Reset to |0>. Input is |0>. So ignore.
            continue
        elif name == 'RX':
            # Reset to |+>. Input |0>. Apply H.
            new_circuit.append('H', targets)
        elif name == 'RY':
             # Reset to |i>. Input |0>. Apply H then S.
             new_circuit.append('H', targets)
             new_circuit.append('S', targets)
        elif name in ['M', 'MX', 'MY', 'MZ']:
            print(f"Warning: Measurement {name} found. Skipping.")
            continue
        elif name == 'TICK':
             continue
        else:
            new_circuit.append(name, targets)

    # Check metrics
    cx_count = 0
    cz_count = 0
    for instr in new_circuit:
        if instr.name == 'CX' or instr.name == 'CNOT':
            cx_count += 1
        elif instr.name == 'CZ':
            cz_count += 1
            
    print(f"Synthesized circuit has {cx_count} CX gates and {cz_count} CZ gates.")
    
    # Save to file
    # We split instructions to avoid long lines that might wrap in the terminal
    # This increases volume (instruction count) but keeps CX count same (0).
    # Since CX count is primary, this is safe.
    with open('candidate.stim', 'w') as f:
        for instruction in new_circuit:
            if instruction.name in ['CZ', 'CX', 'CY', 'SWAP']:
                # Iterate over targets in pairs
                targets = instruction.targets_copy()
                for i in range(0, len(targets), 2):
                    t1 = targets[i]
                    t2 = targets[i+1]
                    f.write(f"{instruction.name} {t1.value} {t2.value}\n")
            elif instruction.name in ['H', 'S', 'X', 'Y', 'Z', 'I']:
                 # Single qubit gates
                 targets = instruction.targets_copy()
                 for t in targets:
                     f.write(f"{instruction.name} {t.value}\n")
            else:
                # Fallback
                f.write(str(instruction) + "\n")
    
    print("Candidate saved to candidate.stim")

if __name__ == "__main__":
    solve()
