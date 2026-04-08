
from current_inputs import CIRCUIT, STABILIZERS
import stim

def generate_circuit():
    circuit = stim.Circuit(CIRCUIT)
    
    start_ancilla = 95
    ancillas = []
    
    # Init ancillas
    # Stim doesn't require explicit init if starting from |0>, but usually good practice.
    # But since we use indices > 94, they are implicitly |0> at start.
    # We can just use them.
    
    # Verification block
    # To minimize depth, we can do H on all ancillas first.
    
    # We need to construct the block carefully.
    # Stim circuit construction is sequential.
    
    # Create a list of operations for the verification
    # We want to interleave the operations as much as possible to keep depth low?
    # Actually, commuting operations can be done in any order.
    # But for a given qubit, operations must be ordered.
    # Since each stabilizer acts on different sets of qubits, we can just append them.
    # But wait, stabilizers overlap!
    # If stabilizers overlap on qubit q, we must order the operations on q.
    # Since all stabilizer checks commute (stabilizers commute), the order of checking S_i vs S_j doesn't matter for the final state,
    # PROVIDED we measure the ancillas.
    # However, if we do `CX a_i q` then `CX a_j q`, the order matters for error propagation.
    # But since they commute, it's fine?
    # `CX a_i q` and `CX a_j q` commute on `q` (Target-Target commute? No!)
    # `CX` and `CX` with same target do NOT commute in general?
    # `CX a q` = $I \otimes |0\rangle\langle 0| + X \otimes |1\rangle\langle 1|$? No.
    # `CX c t`.
    # `CX a_i q` and `CX a_j q`:
    # Matrix multiplication:
    # $CNOT_{13} CNOT_{23}$.
    # They commute. Controls on different qubits, target on same.
    # Yes, CNOTs with same target commute.
    # CZs with same target commute.
    # CYs?
    # `CY a q` = $I \otimes |0\rangle\langle 0| + Y \otimes |1\rangle\langle 1|$.
    # $Y$ and $Y$ commute.
    # $X$ and $Z$ anticommute.
    # So `CX a_i q` and `CZ a_j q` might anticommute?
    # $X$ on target vs $Z$ on target.
    # But `CX` applies X. `CZ` applies Z.
    # $X$ and $Z$ anticommute.
    # So `CX a_i q` and `CZ a_j q` anticommute.
    # BUT, the stabilizers commute.
    # This means if $S_i$ has X on q and $S_j$ has Z on q, there MUST be another qubit p where they also anticommute, cancelling the sign.
    # So the global operators commute.
    # But the individual gates anticommute.
    # Does the order of gates matter?
    # Yes, $A B = - B A$.
    # But we are applying controlled gates.
    # Control is on different ancillas.
    # If ancillas are $|+\rangle$, then we have a superposition of applying $P_i$ and $P_j$.
    # It's known that measuring commuting observables can be done in any order?
    # Yes.
    # So the order of checks shouldn't matter for the *measurement outcome* if no errors.
    # But for *fault tolerance*, order might matter.
    # Since I can't easily optimize, I'll just append them sequentially.
    
    final_circuit = stim.Circuit(CIRCUIT)
    
    # 1. H on all ancillas
    for i in range(len(STABILIZERS)):
        ancilla = start_ancilla + i
        ancillas.append(ancilla)
        final_circuit.append("H", [ancilla])
        
    # 2. Controlled Paulis
    # To keep circuit structure simple, I'll iterate by stabilizer.
    for i, s in enumerate(STABILIZERS):
        ancilla = start_ancilla + i
        # We need to parse the Pauli string
        for q in range(len(s)):
            pauli = s[q]
            if pauli == 'X':
                final_circuit.append("CX", [ancilla, q])
            elif pauli == 'Z':
                final_circuit.append("CZ", [ancilla, q])
            elif pauli == 'Y':
                final_circuit.append("CY", [ancilla, q])
                
    # 3. H on all ancillas
    for i in range(len(STABILIZERS)):
        ancilla = start_ancilla + i
        final_circuit.append("H", [ancilla])
        
    # 4. Measure ancillas
    for i in range(len(STABILIZERS)):
        ancilla = start_ancilla + i
        final_circuit.append("M", [ancilla])
        
    return final_circuit, ancillas

if __name__ == "__main__":
    c, ancillas = generate_circuit()
    print("ANCILLAS:", ancillas)
    # Print circuit to file to avoid console spam?
    with open("candidate.stim", "w") as f:
        f.write(str(c))
