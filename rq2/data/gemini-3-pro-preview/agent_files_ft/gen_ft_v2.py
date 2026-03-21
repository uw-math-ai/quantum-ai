import stim

stabilizers_list = [
    "IIXIXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIXIXXXIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIXIXXXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIXIXXXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXXXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXXX",
    "IXIXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIXIXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIXIXIXXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIXIXIXXIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXXIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXX",
    "XXXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIXXXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIXXXIIXIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIXXXIIXIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXIIXIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXIIXI",
    "IIZIZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIZIZZZIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIZIZZZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIZIZZZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZZZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZZZ",
    "IZIZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIZIZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIZIZIZZIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIZIZIZZIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZZIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZZ",
    "ZZZIIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIZZZIIZIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIZZZIIZIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZZIIZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZIIZIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZIIZI",
    "XXIXIIIXXIXIIIXXIXIIIXXIXIIIXXIXIIIXXIXIII",
    "ZZIZIIIZZIZIIIZZIZIIIZZIZIIIZZIZIIIZZIZIII"
]

def parse_stabilizer(line):
    paulis = []
    for i, char in enumerate(line):
        if char in 'XYZ':
            paulis.append((i, char))
    return paulis

def create_measurement_circuit(stabs, start_ancilla):
    circuit = stim.Circuit()
    ancilla = start_ancilla
    flag_qubits = []

    for stab_str in stabs:
        stab = parse_stabilizer(stab_str)
        if not stab: continue

        # Check type
        is_z = all(p[1] == 'Z' for p in stab)
        is_x = all(p[1] == 'X' for p in stab)
        has_x = any(p[1] == 'X' for p in stab)
        has_z = any(p[1] == 'Z' for p in stab)

        circuit.append("R", [ancilla])
        
        if is_z:
            # Measure Z parity
            for q, p in stab:
                circuit.append("CX", [q, ancilla])
            circuit.append("M", [ancilla])
            flag_qubits.append(ancilla)
            
        elif has_x and not has_z:
            # Measure X parity
            circuit.append("H", [ancilla])
            for q, p in stab:
                circuit.append("CX", [ancilla, q])
            circuit.append("H", [ancilla])
            circuit.append("M", [ancilla])
            flag_qubits.append(ancilla)
            
        else:
            # Mixed? If any mixed, default to X-check style or Z-check style?
            # None in this set.
            pass
        
        ancilla += 1
        
    return circuit, flag_qubits

def main():
    try:
        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\original_circuit.stim", "r") as f:
            content = f.read()
            # Remove comments or newlines if issues? Stim handles it.
            orig_circuit = stim.Circuit(content)
    except Exception as e:
        print(f"Error reading circuit: {e}")
        return

    # Append measurements
    meas_circuit, flags = create_measurement_circuit(stabilizers_list, 42)
    
    full_circuit = orig_circuit + meas_circuit
    
    # Output to file
    out_path = r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\candidate_1.stim"
    with open(out_path, "w") as f:
        f.write(str(full_circuit))
        
    print(f"FLAG_QUBITS: {flags}")
    print(f"Wrote to {out_path}")

if __name__ == "__main__":
    main()
