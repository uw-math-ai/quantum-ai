import stim
import json
import collections

def fix_circuit():
    # Load circuit
    circuit = stim.Circuit.from_file(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\circuit.stim")
    
    # Load bad faults
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\bad_faults.json", "r") as f:
        bad_faults = json.load(f)
        
    # Group faults by op_index
    faults_by_op = collections.defaultdict(list)
    for f in bad_faults:
        faults_by_op[f["op_index"]].append(f)
        
    # Flatten circuit to match op_index
    ops_list = []
    for op in circuit:
        if op.name == "CX" or op.name == "CNOT":
            t = op.targets_copy()
            for k in range(0, len(t), 2):
                ops_list.append( ("CX", [t[k].value, t[k+1].value]) )
        elif op.name in ["H", "X", "Y", "Z", "I"]:
            t = op.targets_copy()
            for k in t:
                ops_list.append( (op.name, [k.value]) )
        else:
            ops_list.append( (op.name, [k.value for k in op.targets_copy()]) )
            
    # Build new circuit
    new_circuit = stim.Circuit()
    
    # Ancilla management
    next_ancilla = 63
    ancillas = []
    
    for i, (name, targets) in enumerate(ops_list):
        # Add original op
        new_circuit.append(name, targets)
        
        # Check if we need flags
        if i in faults_by_op:
            faults = faults_by_op[i]
            # De-duplicate: if multiple faults imply same check
            # Check X on q: need CX q f
            # Check Z on q: need H f, CX f q, H f
            
            checks_needed = set() # (type, qubit)
            for f in faults:
                checks_needed.add((f["fault_type"], f["qubit"]))
                
            for f_type, q in checks_needed:
                anc = next_ancilla
                next_ancilla += 1
                ancillas.append(anc)
                
                if f_type == "X":
                    # Check X on q: CX q anc
                    new_circuit.append("CX", [q, anc])
                elif f_type == "Z":
                    # Check Z on q: H anc, CX anc q, H anc
                    new_circuit.append("H", [anc])
                    new_circuit.append("CX", [anc, q])
                    new_circuit.append("H", [anc])
                    
    # Measure all ancillas
    if ancillas:
        new_circuit.append("M", ancillas)
        
    print(f"Added {len(ancillas)} flags.")
    print(f"Total qubits: {next_ancilla}")
    
    # Save candidate
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\candidate.stim", "w") as f:
        f.write(str(new_circuit))
        
    # Also save ancilla list for return_result
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\ancillas.json", "w") as f:
        json.dump(ancillas, f)

if __name__ == "__main__":
    fix_circuit()
