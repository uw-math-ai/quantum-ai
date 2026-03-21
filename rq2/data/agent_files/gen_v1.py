import stim
import sys

def get_stabilizers():
    # Stabilizers provided in prompt
    # IIXIXXX, IXIXIXX, XXXIIXI, IIZIZZZ, IZIZIZZ, ZZZIIZI
    # Assuming indices 0123456
    return [
        "IIXIXXX",
        "IXIXIXX",
        "XXXIIXI",
        "IIZIZZZ",
        "IZIZIZZ",
        "ZZZIIZI"
    ]

def parse_stabilizer_str(s):
    # Returns list of (qubit_index, pauli_char)
    # Filter out 'I'
    ops = []
    for i, char in enumerate(s):
        if char in ['X', 'Z', 'Y']:
            ops.append((i, char))
    return ops

def generate_circuit_v1():
    # Base circuit
    c = stim.Circuit()
    # CX 2 0 0 2 2 0
    c.append("CX", [2, 0, 0, 2, 2, 0])
    # H 0 1 2
    c.append("H", [0, 1, 2])
    # CX 0 1 0 2 0 5 1 4 1 5 1 6 2 3 2 5 2 6 4 3 3 4 4 3 5 3 6 3 5 4 6 4
    c.append("CX", [0, 1, 0, 2, 0, 5, 1, 4, 1, 5, 1, 6, 2, 3, 2, 5, 2, 6, 4, 3, 3, 4, 4, 3, 5, 3, 6, 3, 5, 4, 6, 4])
    
    # Append verification.
    # We have 6 stabilizers. We need 6 ancillas.
    # Data qubits: 0-6.
    # Ancilla qubits: 7-12.
    
    stabs = [
        "IIXIXXX",
        "IXIXIXX",
        "XXXIIXI",
        "IIZIZZZ",
        "IZIZIZZ",
        "ZZZIIZI"
    ]
    
    # Init ancillas
    for i in range(7, 13):
        c.append("R", [i])
    
    for i, stab_str in enumerate(stabs):
        ancilla = 7 + i
        # Identify Pauli type
        is_x = 'X' in stab_str
        is_z = 'Z' in stab_str
        
        ops = []
        for q_idx, char in enumerate(stab_str):
            if char in ['X', 'Z']:
                ops.append(q_idx)
        
        if is_x:
            # Measure X parity
            # Init |+> on ancilla
            c.append("H", [ancilla])
            # CNOT ancilla -> data (for X check)
            # Correct?
            # Standard X-check:
            # H_a. CNOT(a, d). H_a.
            # Propagates X_a -> X_d.
            # Detects Z_d errors (Z_d -> Z_d Z_a).
            # So checks Z stabilizers?
            # Wait.
            # We want to measure X stabilizer "IIXIXXX".
            # This is an X operator. It detects Z errors.
            # To measure X operator, we need to interact with Z basis of ancilla?
            # No.
            # If we measure Operator O.
            # We prepare ancilla in + eigenstate of X (|+>).
            # Controlled-O.
            # Measure X.
            # If O has eigenvalues +/- 1.
            # If state is +1 eigenstate, ancilla stays |+>.
            # If state is -1 eigenstate, ancilla goes to |->.
            # Controlled-O for Pauli string P = X_i X_j...
            # Controlled-P = Product of Controlled-X.
            # Controlled-X is CNOT.
            # So CNOT(a, d) is Controlled-X on d? Yes.
            # So H_a. CNOT(a, d_i)... H_a. Measure Z_a.
            # This measures the X stabilizer.
            
            for q in ops:
                c.append("CX", [ancilla, q])
            c.append("H", [ancilla])
            c.append("M", [ancilla])
            
        elif is_z:
            # Measure Z parity
            # Init |0> on ancilla.
            # Controlled-Z?
            # No, usually we measure Z parity using CNOTs.
            # CNOT(d, a).
            # If d is |1>, a flips.
            # Parity of |1>s determines final state of a.
            # So CNOT(d, a) measures Z.
            
            for q in ops:
                c.append("CX", [q, ancilla])
            c.append("M", [ancilla])

    return c

if __name__ == "__main__":
    c = generate_circuit_v1()
    print(c)
