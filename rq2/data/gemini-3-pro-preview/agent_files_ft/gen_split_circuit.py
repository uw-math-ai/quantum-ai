import stim
import collections

def generate_split_circuit():
    circuit = stim.Circuit.from_file(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\circuit.stim")
    
    new_circuit = stim.Circuit()
    
    # 1. Initialization
    # We expect RX on data qubits first.
    # We will add R on ancilla qubits.
    
    data_qubits = range(90)
    ancilla_base = 90
    ancillas = [ancilla_base + i for i in data_qubits]
    
    # Add ancilla initialization
    # We'll put it at the beginning or after data init.
    
    # Extract edges from CZ gates
    edges = []
    other_gates = []
    
    has_seen_cz = False
    
    for instr in circuit:
        if instr.name == "CZ":
            has_seen_cz = True
            targets = instr.targets_copy()
            # targets are pairs [t1, t2, t3, t4...]
            for i in range(0, len(targets), 2):
                u = targets[i].value
                v = targets[i+1].value
                edges.append((u, v))
        else:
            if instr.name == "RX":
                new_circuit.append(instr)
                # After RX, init ancillas
                new_circuit.append("R", ancillas)
            elif instr.name == "TICK":
                pass # We manage ticks ourselves
            else:
                other_gates.append(instr)

    # 2. Entangle data and ancillas
    for i in data_qubits:
        new_circuit.append("CX", [i, ancillas[i]])
    
    new_circuit.append("TICK")
    
    # 3. Distribute CZs
    # Greedy allocation
    # phys_degree maps qubit_index -> current degree
    phys_degree = collections.defaultdict(int)
    
    cz_instructions = []
    
    for u, v in edges:
        # Options for u: u or ancilla_u
        # Options for v: v or ancilla_v
        
        opts_u = [u, ancillas[u]]
        opts_v = [v, ancillas[v]]
        
        best_pair = None
        best_score = (float('inf'), float('inf'))
        
        for pu in opts_u:
            for pv in opts_v:
                # Score = max(deg(pu)+1, deg(pv)+1)
                d_pu = phys_degree[pu]
                d_pv = phys_degree[pv]
                score = max(d_pu, d_pv) # We want to minimize the max degree
                
                # Secondary score: sum of degrees
                score2 = d_pu + d_pv
                
                final_score = (score, score2)
                
                if final_score < best_score:
                    best_score = final_score
                    best_pair = (pu, pv)
        
        pu, pv = best_pair
        phys_degree[pu] += 1
        phys_degree[pv] += 1
        cz_instructions.append((pu, pv))
        
    # Append CZs
    # To avoid long lines, we can batch them
    batch = []
    for pu, pv in cz_instructions:
        batch.extend([pu, pv])
        if len(batch) > 100: # chunk
            new_circuit.append("CZ", batch)
            batch = []
    if batch:
        new_circuit.append("CZ", batch)
        
    new_circuit.append("TICK")
        
    # 4. Disentangle / Check
    for i in data_qubits:
        new_circuit.append("CX", [i, ancillas[i]])
        
    new_circuit.append("TICK")
    
    # 5. Measure Ancillas
    new_circuit.append("M", ancillas)
    
    # 6. Apply remaining gates
    for instr in other_gates:
        new_circuit.append(instr)
        
    # Write to file
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\circuit_ft.stim", "w") as f:
        f.write(str(new_circuit))
        
    # Print max degree
    max_deg = max(phys_degree.values()) if phys_degree else 0
    print(f"Max physical degree: {max_deg}")
    print("New circuit generated.")

if __name__ == "__main__":
    generate_split_circuit()
