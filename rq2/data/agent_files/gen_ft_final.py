import stim
import json

def generate_ft_circuit():
    with open("input.stim", "r") as f:
        circuit_text = f.read()
    circuit = stim.Circuit(circuit_text)
        
    num_qubits = 63 
    
    with open("stabilizers.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]
        
    next_ancilla = num_qubits
    
    # We create a separate circuit for checks
    check_circuit = stim.Circuit()
    
    flag_qubits = []
    
    for stab_str in stabs:
        ancilla = next_ancilla
        next_ancilla += 1
        flag_qubits.append(ancilla)
        
        # Init |0> implied for new qubits
        
        # H ancilla
        check_circuit.append("H", [ancilla])
        
        for q_idx, char in enumerate(stab_str):
            if char == 'I':
                continue
            elif char == 'X':
                check_circuit.append("CX", [ancilla, q_idx])
            elif char == 'Z':
                check_circuit.append("CZ", [ancilla, q_idx])
            elif char == 'Y':
                # CY(c, t) = S_DAG(t) CX(c, t) S(t)
                check_circuit.append("S_DAG", [q_idx])
                check_circuit.append("CX", [ancilla, q_idx])
                check_circuit.append("S", [q_idx])
                
        # H ancilla
        check_circuit.append("H", [ancilla])
        
        # Measurement at the end
        check_circuit.append("M", [ancilla])
        
    circuit += check_circuit
    
    return circuit, flag_qubits, stabs

if __name__ == "__main__":
    circuit, flags, stabs = generate_ft_circuit()
    
    with open("candidate.stim", "w") as f:
        f.write(str(circuit))
        
    print(f"Generated circuit with {len(flags)} flags.")
    
    # Also save flag indices for validation
    with open("flags.txt", "w") as f:
        f.write(str(flags))
        
    tool_args = {
        "circuit": str(circuit),
        "data_qubits": list(range(63)),
        "flag_qubits": flags,
        "stabilizers": stabs
    }
    with open("args.json", "w") as f:
        json.dump(tool_args, f)
