import stim
import sys

def cleanup():
    with open('candidate_v54_opt.stim', 'r') as f:
        circ = stim.Circuit(f.read())
    
    touched = set()
    new_circ = stim.Circuit()
    
    for instr in circ:
        if instr.name in ['CX', 'CNOT']:
            targets = instr.targets_copy()
            new_targets = []
            for i in range(0, len(targets), 2):
                c = targets[i].value
                t = targets[i+1].value
                
                c_active = c in touched
                t_active = t in touched
                
                if not c_active:
                    pass
                else:
                    # Control is active. Gate does something.
                    # Target becomes active (if not already).
                    new_targets.append(stim.target_rec(c) if False else c) # Just int
                    new_targets.append(stim.target_rec(t) if False else t) # Just int
                    touched.add(t)
            
            if new_targets:
                new_circ.append(instr.name, new_targets)
                    
        elif instr.name in ['SWAP']:
            pass # Ignore explicit SWAP for now (rare)

        elif instr.name in ['H', 'R', 'RX', 'RY', 'RZ', 'X', 'Y', 'SQRT_X', 'SQRT_Y']:
            # Single qubit gates that change 0 to something else
            new_targets = []
            for t in instr.targets_copy():
                q = t.value
                new_targets.append(q)
                touched.add(q)
            if new_targets:
                new_circ.append(instr.name, new_targets)
                
        elif instr.name in ['I', 'Z', 'S', 'S_DAG', 'SQRT_Z', 'SQRT_Z_DAG']:
            # Identity on 0.
            new_targets = []
            for t in instr.targets_copy():
                q = t.value
                if q in touched:
                    new_targets.append(q)
            if new_targets:
                new_circ.append(instr.name, new_targets)
        else:
            # Measurement etc.
            new_circ.append(instr)
            for t in instr.targets_copy():
                if t.is_qubit_target:
                    touched.add(t.value)

    print(str(new_circ))

if __name__ == "__main__":
    cleanup()
