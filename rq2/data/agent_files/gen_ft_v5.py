import stim
import collections

def main():
    with open("original.stim", "r") as f:
        circuit = stim.Circuit(f.read())

    new_circuit = stim.Circuit()
    
    # Analyze circuit to find segments
    # Data structure: qubit -> current_segment = {'type': 'C'/'T', 'count': int, 'start_op': int, 'end_op': int, 'preceded_by_H': bool}
    # But we need to store COMPLETED segments to process them.
    # segments = list of (qubit, type, start_idx, end_idx, count, preceded_by_H)
    
    segments = []
    current_segments = {} # qubit -> dict
    
    # Track which qubits had H as their last single-qubit gate
    # initialized to False
    last_gate_was_H = collections.defaultdict(bool)
    
    # Helper to close segment
    def close_segment(q, idx):
        if q in current_segments:
            seg = current_segments[q]
            seg['end_idx'] = idx - 1 # ends at previous op
            segments.append(seg)
            del current_segments[q]

    for i, instruction in enumerate(circuit):
        if instruction.name == "CX":
            targets = instruction.targets_copy()
            for j in range(0, len(targets), 2):
                c = targets[j].value
                t = targets[j+1].value
                
                # Update Control c
                if c in current_segments:
                    if current_segments[c]['type'] == 'C':
                        current_segments[c]['count'] += 1
                    else:
                        close_segment(c, i)
                        current_segments[c] = {'qubit': c, 'type': 'C', 'count': 1, 'start_idx': i, 'preceded_by_H': last_gate_was_H[c]}
                else:
                    current_segments[c] = {'qubit': c, 'type': 'C', 'count': 1, 'start_idx': i, 'preceded_by_H': last_gate_was_H[c]}
                
                # Update Target t
                if t in current_segments:
                    if current_segments[t]['type'] == 'T':
                        current_segments[t]['count'] += 1
                    else:
                        close_segment(t, i)
                        current_segments[t] = {'qubit': t, 'type': 'T', 'count': 1, 'start_idx': i, 'preceded_by_H': last_gate_was_H[t]}
                else:
                    current_segments[t] = {'qubit': t, 'type': 'T', 'count': 1, 'start_idx': i, 'preceded_by_H': last_gate_was_H[t]}
            
            # Note: CX does not reset "last_gate_was_H" for C or T? 
            # Usually H -> CX -> ...
            # The H status persists until another single qubit gate.
            
        elif instruction.name in ["H", "R", "M", "X", "Y", "Z", "RX", "RY", "RZ", "MX", "MY", "MZ"]:
            # Single qubit gates (or mostly single)
            # Close segments for all targets
            targets = instruction.targets_copy()
            for t_obj in targets:
                t = t_obj.value
                close_segment(t, i)
                if instruction.name == "H":
                    last_gate_was_H[t] = True
                else:
                    last_gate_was_H[t] = False
        else:
            # Other gates? 
            pass

    # Close all at end
    final_idx = len(circuit)
    for q in list(current_segments.keys()):
        close_segment(q, final_idx)

    # Filter segments
    # Threshold 4
    THRESHOLD = 4
    critical_segments = [s for s in segments if s['count'] >= THRESHOLD]
    
    insertions_map = collections.defaultdict(list) # index -> list of instruction strings
    
    next_ancilla = 63
    
    # Helper to add insertion
    def add_insert(idx, op_str):
        insertions_map[idx].append(op_str)
        
    for seg in critical_segments:
        q = seg['qubit']
        start = seg['start_idx']
        end = seg['end_idx'] # inclusive
        
        # Determine gadget
        # Case 1: Control (X-spread)
        if seg['type'] == 'C':
            # Gadget: Wrap with CX q f.
            # Start/End Flags
            f_wrap = next_ancilla
            next_ancilla += 1
            
            # Wrap Start
            add_insert(start, f"CX {q} {f_wrap}")
            
            # Wrap End (after end_idx, i.e. at end_idx + 1)
            add_insert(end + 1, f"CX {q} {f_wrap}")
            add_insert(end + 1, f"M {f_wrap}")
            
            # Prep Check
            # If preceded_by_H, add verification.
            if seg['preceded_by_H']:
                f_prep = next_ancilla
                next_ancilla += 1
                # Check for X-error from H: use CX q f_prep.
                add_insert(start, f"CX {q} {f_prep}")
                add_insert(start, f"M {f_prep}")

        # Case 2: Target (Z-spread)
        elif seg['type'] == 'T':
            # Gadget: Wrap with H f, CX f q, H f.
            
            f_wrap = next_ancilla
            next_ancilla += 1
            
            # Wrap Start
            add_insert(start, f"H {f_wrap}")
            add_insert(start, f"CX {f_wrap} {q}")
            
            # Wrap End
            add_insert(end + 1, f"CX {f_wrap} {q}")
            add_insert(end + 1, f"H {f_wrap}")
            add_insert(end + 1, f"M {f_wrap}")
            
            # Prep Check (if preceded by H? H converts X->Z, so yes)
            if seg['preceded_by_H']:
                 f_prep = next_ancilla
                 next_ancilla += 1
                 # Check for Z-error (or X-error after H? Wait. H converts Z to X. If we check Z on q after H, we check X before H.)
                 # The danger is Z error on q (Target).
                 # So we check Z on q.
                 # Gadget: H f, CX f q, H f.
                 add_insert(start, f"H {f_prep}")
                 add_insert(start, f"CX {f_prep} {q}")
                 add_insert(start, f"H {f_prep}")
                 add_insert(start, f"M {f_prep}")

    # Construct new circuit
    for i in range(len(circuit) + 1):
        # Add insertions for this index
        if i in insertions_map:
            for op_str in insertions_map[i]:
                new_circuit.append_from_stim_program_text(op_str)
        
        # Add original instruction
        if i < len(circuit):
            new_circuit.append(circuit[i])
            
    print(new_circuit)

if __name__ == "__main__":
    main()
