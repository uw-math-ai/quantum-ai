import stim

def generate_circuit():
    original_path = "data/gemini-3-pro-preview/agent_files_ft/original.stim"
    stabs_path = "data/gemini-3-pro-preview/agent_files_ft/stabilizers_correct.txt"
    
    with open(original_path, 'r') as f:
        circ = stim.Circuit(f.read())
        
    with open(stabs_path, 'r') as f:
        lines = [l.strip().replace(',','').replace(' ','') for l in f if l.strip()]
    stabs = [stim.PauliString(l) for l in lines]
    
    all_stabs = [(s, 0) for s in stabs]
    
    log_op = stim.PauliString(45)
    for k in [15,16,17,24,25,26]: log_op[k] = 1
    for k in [36,40,44]: log_op[k] = 3
    all_stabs.append((log_op, 1))
    
    new_circ = stim.Circuit()
    new_circ += circ
    
    qubit_offset = 45
    def get_ancillas(n):
        nonlocal qubit_offset
        anc = list(range(qubit_offset, qubit_offset+n))
        qubit_offset += n
        return anc

    for stab, expected in all_stabs:
        w = stab.weight
        support = [q for q in range(45) if stab[q] != 0]
        
        has_x = False
        has_z = False
        for q in support:
            p = stab[q]
            if p == 1 or p == 2: has_x = True
            if p == 3 or p == 2: has_z = True
            
        if w <= 4:
            anc = get_ancillas(1)[0]
            new_circ.append("R", [anc])
            new_circ.append("H", [anc])
            for q in support:
                p = stab[q]
                if p == 1: new_circ.append("CX", [anc, q])
                elif p == 2: new_circ.append("CY", [anc, q])
                elif p == 3: new_circ.append("CX", [q, anc]) # CZ
            new_circ.append("H", [anc])
            if expected == 1: new_circ.append("X", [anc])
            new_circ.append("M", [anc])
            
        else:
            anc = get_ancillas(1)[0]
            new_circ.append("R", [anc])
            new_circ.append("H", [anc])
            
            # Split support into chunks of 4 (max spread 4)
            # We need to flag after each chunk except last?
            # 12 -> 4, 4, 4. Flag after 1, Flag after 2.
            # Errors in 3rd chunk spread 4. Safe.
            
            chunk_size = 4
            num_chunks = (len(support) + chunk_size - 1) // chunk_size
            
            flags_list = []
            
            for i in range(num_chunks):
                is_last = (i == num_chunks - 1)
                
                # Setup flags for this boundary (before applying chunk)
                # But flags check the *previous* application?
                # No.
                # `CX anc f` -> `Apply Chunk` -> `CX anc f`.
                # This checks if error happened *during* Chunk application.
                # So we wrap EACH chunk with flags?
                # Yes.
                # Wait. If error happens *during* chunk 1. It propagates to f1.
                # And propagates to chunk 2, 3...
                # Total weight > 4. Caught by f1.
                # If error happens *during* chunk 2. Propagates to f2.
                # And propagates to chunk 3 (weight 4).
                # Total weight 4 + error on f2.
                # Wait. Error on `anc` propagates to chunk 2 qubits (up to 4).
                # And to chunk 3 qubits (up to 4).
                # Total 8.
                # So error in chunk 2 is bad.
                # Unless we catch it!
                # f2 catches it?
                # `CX anc f2` -> `Apply Chunk 2` -> `CX anc f2`.
                # If error happens during Chunk 2:
                # Caught by f2?
                # Yes.
                # So we wrap EVERY chunk with flags?
                # But the last chunk (3) error spreads only to itself (4). So safe.
                # So wrap all chunks EXCEPT last one.
                
                chunk = support[i*chunk_size : (i+1)*chunk_size]
                
                current_flags = []
                if not is_last:
                    if has_x:
                        f = get_ancillas(1)[0]
                        new_circ.append("R", [f]) # 0
                        new_circ.append("CX", [anc, f])
                        current_flags.append(('x', f))
                    if has_z:
                        f = get_ancillas(1)[0]
                        new_circ.append("R", [f]) # 0
                        new_circ.append("H", [f]) # +
                        new_circ.append("CX", [f, anc])
                        current_flags.append(('z', f))
                
                # Apply chunk
                for q in chunk:
                    p = stab[q]
                    if p == 1: new_circ.append("CX", [anc, q])
                    elif p == 2: new_circ.append("CY", [anc, q])
                    elif p == 3: new_circ.append("CX", [q, anc])
                
                # Uncompute flags
                if not is_last:
                    for f_type, f in current_flags:
                        if f_type == 'x': new_circ.append("CX", [anc, f])
                        elif f_type == 'z': new_circ.append("CX", [f, anc])
                    flags_list.extend(current_flags)

            new_circ.append("H", [anc])
            if expected == 1: new_circ.append("X", [anc])
            
            # Measure anc
            meas_targets = [anc]
            # Measure flags
            for f_type, f in flags_list:
                if f_type == 'x':
                    meas_targets.append(f) # Measure Z
                elif f_type == 'z':
                    new_circ.append("H", [f]) # Measure X
                    meas_targets.append(f)
            
            new_circ.append("M", meas_targets)

    return str(new_circ)

if __name__ == "__main__":
    print(generate_circuit())
