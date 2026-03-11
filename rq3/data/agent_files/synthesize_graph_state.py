import stim
import sys

def solve():
    # Read stabilizers
    with open("target_stabilizers_v2.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]

    # Create tableau
    paulis = [stim.PauliString(s) for s in stabs]
    tableau = stim.Tableau.from_stabilizers(paulis, allow_underconstrained=True)
    print(f"Tableau qubits: {len(tableau)}")
    
    # Synthesize circuit
    # method='graph_state' produces a circuit with H, S, CZ, and RX gates.
    # It is optimal for CX count (0 CXs, only CZs).
    circuit = tableau.to_circuit(method="graph_state")
    
    # Post-process to remove RX (resets) if any, replacing with H (assuming start |0>)
    # Also we might want to decompose CZ to CX if the metric penalizes CZ heavily in volume,
    # but the primary metric is CX count. CZ has 0 CX cost. 
    # Wait, does evaluate_optimization count CZ as CX?
    # The prompt says: "cx_count – number of CX (CNOT) gates".
    # And "volume – total gate count in the volume gate set (CX, CY, CZ, H, S, SQRT_X, etc.)".
    # So CZ contributes to volume but not cx_count. This is good!
    
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            # Replace RX with H
            # RX resets to |+>. Since we start at |0>, H also goes to |+>.
            targets = instruction.targets_copy()
            new_circuit.append("H", targets)
        else:
            new_circuit.append(instruction)
            
    # Check metrics
    cx_count = 0
    for instr in new_circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            cx_count += len(instr.targets_copy()) // 2
            
    print(f"Candidate CX count: {cx_count}")
    
    with open("candidate.stim", "w") as f:
        f.write(str(new_circuit))

if __name__ == "__main__":
    solve()
