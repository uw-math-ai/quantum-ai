import sys
import math

def generate_ft_circuit():
    circuit_base = """H 0 1 2 3 5 8 10 11 12 20 24
CX 0 1 0 2 0 3 0 5 0 8 0 10 0 11 0 12 0 15 0 20 0 23 0 24
H 22
CX 10 0 20 0 22 0 15 1 1 15 15 1
H 1
CX 1 23 5 1 20 1 22 1 5 2 2 5 5 2
H 2
CX 2 23
S 10 20
H 3 5 8 10 11 12 15 20 24
CX 3 2 5 2 8 2 10 2 11 2 12 2 15 2 20 2 22 2 24 2 10 3 3 10 10 3
S 3
H 3
S 3
H 20 23
CX 20 3 22 3 23 3 20 4 4 20 20 4
S 4
H 5 8 10 11 12 15 23 24
CX 4 5 4 8 4 10 4 11 4 12 4 15 4 23 4 24
H 23
CX 22 4 23 4 11 5 5 11 11 5
H 6 14 20
CX 5 6 5 8 5 10 5 14 5 15 5 16 5 20 5 23 5 24
H 21
CX 15 5 21 5 23 5 16 6 6 16 16 6
H 6 15
CX 6 15 16 6 21 6 23 6 15 7 7 15 15 7
H 16
CX 7 16 21 7 23 7 16 8 8 16 16 8
S 8
H 8
S 8 23
H 10 14 16 20 23 24
CX 10 8 14 8 16 8 20 8 21 8 23 8 24 8 23 9 9 23 23 9
H 9
S 9
H 10 14 16 20 24
CX 9 10 9 14 9 16 9 20 9 24 21 9 11 10 10 11 11 10
H 13 15 21 24
CX 10 11 10 12 10 13 10 14 10 15 10 17 10 20 10 21 10 22 10 24 12 10 22 10 17 11 11 17 17 11
H 11
CX 11 21 15 11 22 11 15 12 12 15 15 12
H 12
CX 12 21
S 15 22
H 13 14 15 17 20 22 24
CX 13 12 14 12 15 12 17 12 20 12 22 12 24 12 15 13 13 15 15 13
S 13
H 13
S 13
H 21 22
CX 21 13 22 13 22 14 14 22 22 14
S 14
H 15 17 20 21 22 24
CX 14 15 14 17 14 20 14 21 14 22 14 24
H 21
CX 21 14
H 21 24
CX 15 18 15 21 15 24 17 15 18 16 16 18 18 16
H 16 17 24
CX 16 17 16 21 16 24 18 16
H 18
CX 17 18 17 21
H 21 24
CX 21 17 24 17 24 18 18 24 24 18
H 18 21
CX 18 21 18 24
H 21 24
CX 21 18 24 18 24 19 19 24 24 19
H 21
CX 19 21
H 21 23
CX 20 21 20 22 20 23 20 24 21 20 22 20 24 21 21 24 24 21
H 21
CX 23 21 24 21 23 22 22 23 23 22
H 22
S 23 24
H 23 24
CX 23 22 24 22
S 23
H 23
S 23
H 24
CX 24 23
S 24
H 2 3 7 13 17 22
S 2 2 3 3 7 7 13 13 17 17 22 22
H 2 3 7 13 17 22
S 2 2 4 4 5 5 7 7 9 9 11 11 12 12 13 13 14 14 15 15 17 17 20 20 21 21 22 22 23 23 24 24"""

    stabilizers = [
        "XZZXIIIIIIIIIIIIIIIIIIIII", "IIIIIXZZXIIIIIIIIIIIIIIII", "IIIIIIIIIIXZZXIIIIIIIIIII", "IIIIIIIIIIIIIIIXZZXIIIIII", "IIIIIIIIIIIIIIIIIIIIXZZXI", "IXZZXIIIIIIIIIIIIIIIIIIII",
        "IIIIIIXZZXIIIIIIIIIIIIIII", "IIIIIIIIIIIXZZXIIIIIIIIII", "IIIIIIIIIIIIIIIIXZZXIIIII", "IIIIIIIIIIIIIIIIIIIIIXZZX", "XIXZZIIIIIIIIIIIIIIIIIIII", "IIIIIXIXZZIIIIIIIIIIIIIII",
        "IIIIIIIIIIXIXZZIIIIIIIIII", "IIIIIIIIIIIIIIIXIXZZIIIII", "IIIIIIIIIIIIIIIIIIIIXIXZZ", "ZXIXZIIIIIIIIIIIIIIIIIIII", "IIIIIZXIXZIIIIIIIIIIIIIII", "IIIIIIIIIIZXIXZIIIIIIIIII",
        "IIIIIIIIIIIIIIIZXIXZIIIII", "IIIIIIIIIIIIIIIIIIIIZXIXZ", "XXXXXZZZZZZZZZZXXXXXIIIII", "IIIIIXXXXXZZZZZZZZZZXXXXX", "XXXXXIIIIIXXXXXZZZZZZZZZZ", "ZZZZZXXXXXIIIIIXXXXXZZZZZ"
    ]

    new_circuit_lines = circuit_base.strip().split('\n')
    ancilla_idx = 25
    flag_qubits = []

    for stab in stabilizers:
        meas_ancilla = ancilla_idx
        ancilla_idx += 1
        flag_qubits.append(meas_ancilla)
        
        # Build ops list
        ops = []
        for q, p in enumerate(stab):
            if p == 'X':
                ops.append(f"CX {meas_ancilla} {q}")
            elif p == 'Z':
                ops.append(f"CZ {meas_ancilla} {q}")
        
        # Determine chunks
        chunk_size = 3
        num_ops = len(ops)
        # We need (num_ops + chunk_size - 1) // chunk_size chunks.
        # But wait, if num_ops is 4. 4 // 3 = 1 remainder 1. 2 chunks.
        # Chunk 1 (3 ops), Flag, Chunk 2 (1 op).
        # Unflagged: Chunk 2 (1 op). Safe.
        
        # Prepare Measurement Ancilla
        new_circuit_lines.append(f"H {meas_ancilla}")

        # Iterate through chunks
        current_op_idx = 0
        while current_op_idx < num_ops:
            # Check if this is the last chunk
            is_last = (current_op_idx + chunk_size) >= num_ops
            
            # Add ops for this chunk
            end_idx = min(current_op_idx + chunk_size, num_ops)
            for i in range(current_op_idx, end_idx):
                new_circuit_lines.append(ops[i])
            
            current_op_idx = end_idx
            
            # If not last, add a flag
            if not is_last:
                flg = ancilla_idx
                ancilla_idx += 1
                flag_qubits.append(flg)
                new_circuit_lines.append(f"H {flg}")
                new_circuit_lines.append(f"CZ {meas_ancilla} {flg}") # Flag interaction
                new_circuit_lines.append(f"H {flg}")
                new_circuit_lines.append(f"M {flg}")
                # We can measure flag immediately to reuse? No, prompt says measure at end.
                # But it says "initialized... and measured at the end".
                # If I measure it now, it's not "at the end".
                # But physically, it's fine.
                # However, to be safe with "measured at the end" rule, I should NOT measure now.
                # I'll measure all at the very end.
        
        # Measure Measurement Ancilla
        new_circuit_lines.append(f"H {meas_ancilla}")
        new_circuit_lines.append(f"M {meas_ancilla}")

    # Move all measurements to the end?
    # The prompt says "measured at the end".
    # This might mean "after all gates".
    # My current code interleaves measurements.
    # I should collect all measurements and put them at the end.
    
    # Actually, let's just make the circuit string and then move M gates to bottom.
    final_lines = []
    measurements = []
    for line in new_circuit_lines:
        if line.startswith("M "):
            measurements.append(line)
        else:
            final_lines.append(line)
    
    final_lines.extend(measurements)
    
    print("\n".join(final_lines))
    print(f"# FLAGS: {','.join(map(str, flag_qubits))}")

if __name__ == "__main__":
    generate_ft_circuit()
