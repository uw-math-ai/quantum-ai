import stim
import sys

def fix_circuit():
    try:
        with open("input_current.stim", "r") as f:
            content = f.read()
    except FileNotFoundError:
        print("input_current.stim not found")
        return

    circuit = stim.Circuit(content)
    
    new_circuit = stim.Circuit()
    
    # Ancilla allocation
    # Start high enough to avoid collision with data qubits
    next_ancilla = 175
    
    # We process the circuit in blocks of CNOTs
    current_block = []
    
    def flush_block():
        nonlocal next_ancilla
        if not current_block:
            return
        
        output_block = []
        
        # State for the block
        active_copy = {} # q -> current_node
        copy_usage = {} # node -> count
        copies_map = {} # q -> list of nodes [q, a1, a2...]
        
        def get_current_node(q):
            if q not in active_copy:
                active_copy[q] = q
                copy_usage[q] = 0
                copies_map[q] = [q]
            return active_copy[q]
            
        def spawn_copy(q):
            nonlocal next_ancilla
            curr = get_current_node(q)
            new_a = next_ancilla
            next_ancilla += 1
            
            # Source split (Control)
            # CX curr new_a
            output_block.append(stim.CircuitInstruction("CX", [curr, new_a]))
            
            active_copy[q] = new_a
            copy_usage[new_a] = 0
            copies_map[q].append(new_a)
            
        def merge_copies(q):
            if q not in copies_map:
                return
            
            nodes = copies_map[q]
            # Merge back in reverse order
            for i in range(len(nodes)-1, 0, -1):
                src = nodes[i-1]
                dst = nodes[i]
                output_block.append(stim.CircuitInstruction("CX", [src, dst]))
                
            # Reset
            active_copy[q] = q
            copy_usage[q] = 0
            copies_map[q] = [q]
            
        
        for op in current_block:
            if op.name == "CX":
                targets = op.targets_copy()
                for i in range(0, len(targets), 2):
                    c = targets[i].value
                    t = targets[i+1].value
                    
                    # If t is being modified (target), merge copies of t
                    merge_copies(t)
                    
                    # Determine current control node
                    c_node = get_current_node(c)
                    
                    # Check load (limit 6)
                    if copy_usage[c_node] >= 6:
                        spawn_copy(c)
                        c_node = get_current_node(c)
                        
                    copy_usage[c_node] += 1
                    
                    output_block.append(stim.CircuitInstruction("CX", [c_node, t]))
            else:
                output_block.append(op)
                
        # End of block: Merge all remaining copies
        for q in list(copies_map.keys()):
            merge_copies(q)
            
        for op in output_block:
            new_circuit.append(op)
            
        current_block.clear()

    # Iterate over circuit
    for op in circuit:
        if op.name == "CX":
            current_block.append(op)
        else:
            flush_block()
            
            # Insert check before H? No, H initializes.
            # Insert check AFTER H.
            new_circuit.append(op)
            
            if op.name == "H":
                targets = op.targets_copy()
                for t in targets:
                    val = t.value
                    # Check gadget: H f, CZ f val, H f, M f
                    f_anc = next_ancilla
                    next_ancilla += 1
                    
                    new_circuit.append("H", [f_anc])
                    new_circuit.append("CZ", [f_anc, val])
                    new_circuit.append("H", [f_anc])
                    
                    # We will measure f_anc at the end

    flush_block()
    
    # Measure all ancillas
    if next_ancilla > 175:
        ancillas = list(range(175, next_ancilla))
        for i in range(0, len(ancillas), 10):
            chunk = ancillas[i:i+10]
            new_circuit.append("M", chunk)

    with open("candidate.stim", "w") as f:
        f.write(str(new_circuit))
        
    print(f"Generated candidate.stim with {next_ancilla - 175} ancillas")

if __name__ == "__main__":
    fix_circuit()
