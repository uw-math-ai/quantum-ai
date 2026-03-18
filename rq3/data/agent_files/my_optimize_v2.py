import stim

baseline_str = """
CX 1 0 0 1 1 0
H 0
CX 0 3 0 4
H 1
CX 1 0 1 4 1 6 4 2 2 4 4 2 5 2 6 2 4 3 3 4 4 3
H 3
CX 3 5 3 6 4 5 6 4 6 5 5 6 6 5
"""

target_stabilizers = [
    "XXIIXXI", "XIXIXIX", "IIIXXXX",
    "ZZIIZZI", "ZIZIZIZ", "IIIZZZZ"
]

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            count += len(instr.targets_copy()) // 2
    return count

def check_preservation(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    preserved = 0
    for s_str in stabilizers:
        s = stim.PauliString(s_str)
        if sim.peek_observable_expectation(s) == 1:
            preserved += 1
    return preserved == len(stabilizers)

def apply_permutation(circuit, p_map):
    # p_map[i] is destination of content at i
    # We implement the permutation defined by p_map on the physical wires 0..6
    # p_map must be a permutation of 0..6
    
    visited = set()
    cycles = []
    
    # Find cycles
    for i in range(7):
        if i in visited: continue
        
        cycle = []
        curr = i
        while curr not in visited:
            visited.add(curr)
            cycle.append(curr)
            curr = p_map[curr]
        cycles.append(cycle)

    # Apply swaps for each cycle
    for cycle in cycles:
        if len(cycle) < 2: continue
        
        # Cycle: c0 -> c1 -> c2 ... -> ck -> c0
        # SWAP(c0, c1), SWAP(c0, c2), ..., SWAP(c0, ck)
        
        c0 = cycle[0]
        for j in range(1, len(cycle)):
            cj = cycle[j]
            # Use 3 CX for SWAP
            circuit.append("CX", [c0, cj, cj, c0, c0, cj])

def optimize_with_swap_removal():
    new_circuit = stim.Circuit()
    
    # p_base tracks logical -> physical in BASELINE execution
    p_base = {i: i for i in range(7)}
    
    def get_log_at_base(phys):
        for l, ph in p_base.items():
            if ph == phys: return l
        return -1
    
    def emit_gate(name, targets):
        # In NEW circuit, logical L is at physical L.
        # So if baseline says "Gate on phys P", it means "Gate on logical L=p_base_inv[P]".
        # So we emit "Gate on L".
        new_targets = []
        for t in targets:
            L = get_log_at_base(t)
            new_targets.append(L)
        new_circuit.append(name, new_targets)
        
    def base_swap(a, b):
        # Update p_base (baseline does a swap)
        la = get_log_at_base(a)
        lb = get_log_at_base(b)
        p_base[la] = b
        p_base[lb] = a

    # Trace baseline instructions
    
    # 1. SWAP 0 1
    base_swap(0, 1)
    
    # 2. H 0
    emit_gate("H", [0])
    
    # 3. CX 0 3 0 4
    emit_gate("CX", [0, 3, 0, 4])
    
    # 4. H 1
    emit_gate("H", [1])
    
    # 5. CX 1 0 1 4 1 6
    emit_gate("CX", [1, 0, 1, 4, 1, 6])
    
    # 6. SWAP 2 4
    base_swap(2, 4)
    
    # 7. CX 5 2 6 2
    emit_gate("CX", [5, 2, 6, 2])
    
    # 8. SWAP 3 4
    base_swap(3, 4)
    
    # 9. H 3
    emit_gate("H", [3])
    
    # 10. CX 3 5 3 6
    emit_gate("CX", [3, 5, 3, 6])
    
    # 11. CX 4 5
    emit_gate("CX", [4, 5])
    
    # 12. CX 6 4
    emit_gate("CX", [6, 4])
    
    # 13. SWAP 5 6
    base_swap(5, 6)
    
    # Now fix permutation
    # Current state: logical L is at physical L.
    # Desired state: logical L is at physical p_base[L].
    # So we want to map L -> p_base[L].
    apply_permutation(new_circuit, p_base)
    
    return new_circuit

base = stim.Circuit(baseline_str)
print(f"Baseline CX count: {count_cx(base)}")
# print(f"Baseline valid: {check_preservation(base, target_stabilizers)}")

opt = optimize_with_swap_removal()
print(f"Optimized CX count: {count_cx(opt)}")
print(f"Optimized valid: {check_preservation(opt, target_stabilizers)}")
print("Optimized circuit:")
print(opt)
