import sys
import re

# Increase recursion depth just in case
sys.setrecursionlimit(2000)

def parse_circuit(circuit_str):
    ops = []
    for line in circuit_str.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        gate = parts[0]
        targets = []
        for p in parts[1:]:
            try:
                targets.append(int(p))
            except ValueError:
                pass # ignore comments or invalid
        
        # Split multi-target gates into individual operations
        if gate in ['H', 'S', 'X', 'Y', 'Z', 'M', 'R']:
            for t in targets:
                ops.append((gate, [t]))
        elif gate == 'CX':
            if len(targets) % 2 != 0:
                raise ValueError(f"CX gate has odd number of targets: {line}")
            for i in range(0, len(targets), 2):
                ops.append((gate, [targets[i], targets[i+1]]))
        else:
            raise ValueError(f"Unknown gate: {gate}")
            
    return ops

def to_stim_string(ops):
    lines = []
    for gate, targets in ops:
        t_str = " ".join(str(t) for t in targets)
        lines.append(f"{gate} {t_str}")
    return "\n".join(lines)

def analyze_and_insert_flags(ops, num_data_qubits):
    new_ops = []
    next_flag = num_data_qubits
    flag_qubits = []
    
    # active_ancillas[q] = {'ancilla': a, 'count': 0}
    active_ancillas = {}
    
    def flush_ancilla(q):
        added = []
        if q in active_ancillas:
            info = active_ancillas[q]
            a = info['ancilla']
            added.append(('CX', [q, a]))
            # Note: We do NOT measure 'a' here, we assume user adds M later?
            # No, we should measure here to reuse ancilla?
            # Or assume unique flags?
            # Script uses unique flags.
            # But the prompt requires "measured at the end".
            # So we should not measure here?
            # But if we don't measure here, we can't detect intermediate errors.
            # We just need to ensure 'a' is measured eventually.
            # Since 'a' is unique, we can leave M for the end loop in main.
            # BUT we need to flag the error.
            # If we uncompute 'a', it holds the error info (if any).
            # So measuring at the end is fine.
            del active_ancillas[q]
        return added

    for gate, targets in ops:
        involved = []
        if gate == 'CX':
            involved = targets
        elif gate in ['H', 'S', 'X', 'Y', 'Z', 'M', 'R']:
            involved = targets
            
        # Flush if any involved qubit (except Control in CX) changes role
        # Actually, simpler: Flush ALL involved before operation, unless reusing.
        
        if gate == 'CX':
            c, t = targets
            # Check if t needs flush
            if t in active_ancillas:
                new_ops.extend(flush_ancilla(t))
                
            # Check if c needs flush (if count full)
            if c in active_ancillas:
                if active_ancillas[c]['count'] >= 2:
                    new_ops.extend(flush_ancilla(c))
                    
            # Allocate if needed
            if c not in active_ancillas:
                a = next_flag
                next_flag += 1
                flag_qubits.append(a)
                active_ancillas[c] = {'ancilla': a, 'count': 0}
                new_ops.append(('CX', [c, a]))
                
            # Use ancilla
            a = active_ancillas[c]['ancilla']
            new_ops.append(('CX', [a, t]))
            active_ancillas[c]['count'] += 1
            
        else:
            # Flush all involved
            for q in involved:
                if q in active_ancillas:
                    new_ops.extend(flush_ancilla(q))
            new_ops.append((gate, targets))
            
    # Flush remaining
    for q in list(active_ancillas.keys()):
        new_ops.extend(flush_ancilla(q))
        
    return new_ops, flag_qubits

def main():
    with open('baseline_mine.stim', 'r') as f:
        circuit_str = f.read()
    
    ops = parse_circuit(circuit_str)
    
    # Data qubits 0-62
    num_data_qubits = 63
    
    new_ops, flag_qubits = analyze_and_insert_flags(ops, num_data_qubits)
    
    # Add measurements for flags
    # We must also measure all data qubits if they are not already measured?
    # But usually validate_circuit handles state verification.
    # The prompt says: "All ancilla qubits must be initialized in the |0> state and measured at the end of the circuit."
    # The data qubits prepare a state, so they are not measured.
    # But flag qubits are ancillas.
    for f in flag_qubits:
        new_ops.append(('M', [f]))
        
    candidate_str = to_stim_string(new_ops)
    
    with open('candidate_mine.stim', 'w') as f:
        f.write(candidate_str)
        
    # Print flag info for my parsing in tool call
    print(f"FLAG_QUBITS:{flag_qubits}")

if __name__ == '__main__':
    main()
