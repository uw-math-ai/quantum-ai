import stim
import sys

def optimize_tail(circuit_str):
    circuit = stim.Circuit(circuit_str)
    
    # Separate into head (up to last 2-qubit gate) and tail
    # We iterate and find the index of the last 2-qubit gate.
    
    last_2q_index = -1
    for i, instr in enumerate(circuit):
        if len(instr.targets_copy()) > 1:
            # Check if it's actually a 2-qubit gate (like CZ, CX)
            # RX with multiple targets is multiple 1-qubit gates.
            # CZ with multiple targets is multiple 2-qubit gates.
            # But in the flat list, CZ 0 3 is one instruction with 2 targets.
            # Wait, my candidate has CZ 0 3 as one instruction.
            # But if I have "RX 0 1", it's 1-qubit gate on multiple qubits.
            
            name = instr.name
            if name in ["CX", "CZ", "CNOT", "SWAP", "ISWAP", "CV", "CY"]:
                last_2q_index = i
            
    # If no 2q gates, head is empty?
    # Actually, if we have CZs, we split there.
    
    head = stim.Circuit()
    tail_ops = []
    
    for i, instr in enumerate(circuit):
        if i <= last_2q_index:
            head.append(instr)
        else:
            tail_ops.append(instr)
            
    # Now process tail_ops
    # We want to group by qubit.
    # But wait, gates on different qubits commute.
    # Gates on same qubit must be ordered.
    
    qubit_ops = {} # qubit -> stim.Circuit (sequence of ops)
    
    for instr in tail_ops:
        name = instr.name
        for t in instr.targets_copy():
            q = t.value
            if q not in qubit_ops:
                qubit_ops[q] = stim.Circuit()
            # Append single gate
            qubit_ops[q].append(name, [q])
            
    # Now fuse
    optimized_tail = stim.Circuit()
    
    # We want deterministic output, so sort qubits
    all_qubits = sorted(qubit_ops.keys())
    
    for q in all_qubits:
        ops = qubit_ops[q]
        # Build mini circuit for qubit 0
        sub_circuit = stim.Circuit()
        for instr in ops:
            sub_circuit.append(instr.name, [0])
            
        t = stim.Tableau.from_circuit(sub_circuit)
        fused = t.to_circuit()
        
        for fused_instr in fused:
            # Map back to q
            # fused_instr target is 0
            optimized_tail.append(fused_instr.name, [q])
            
    # Combine
    full_circuit = head + optimized_tail
    return full_circuit

def print_circuit_safely(circuit):
    for instruction in circuit:
        if instruction.name == "TICK":
            continue
        
        name = instruction.name
        targets = instruction.targets_copy()
        qubits = [t.value for t in targets]
        
        if name in ["CX", "CZ", "SWAP", "CNOT", "CY", "ISWAP"]:
            # 2-qubit gates
            for i in range(0, len(qubits), 2):
                print(f"{name} {qubits[i]} {qubits[i+1]}")
        else:
            # 1-qubit gates or others
            # Print individually to avoid wrapping
            for q in qubits:
                print(f"{name} {q}")

# Read from file
with open("candidate_agent.stim", "r") as f:
    content = f.read()

new_circuit = optimize_tail(content)
print_circuit_safely(new_circuit)
