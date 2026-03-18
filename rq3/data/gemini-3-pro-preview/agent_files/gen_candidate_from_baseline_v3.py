import stim
import os

# Create directory
os.makedirs("data/gemini-3-pro-preview/agent_files", exist_ok=True)

try:
    # Load baseline
    with open("baseline.stim", "r") as f:
        baseline_text = f.read()
    baseline = stim.Circuit(baseline_text)
    
    # Simulate to get tableau
    sim = stim.TableauSimulator()
    sim.do(baseline)
    tableau = sim.current_inverse_tableau().inverse()
    
    # Synthesize new circuit
    # Use graph_state method which uses CZ and single qubit gates (no CX)
    circuit = tableau.to_circuit(method="graph_state")
    
    # Process resets (replace RX with H, remove R/RZ, replace RY)
    # Graph state synthesis typically produces a circuit that starts with resets (RX/RY/RZ) 
    # then gates to prepare the state.
    # Since we start from |0>, we need to map the resets to unitary operations on |0>.
    # RX means prepare |+>. H |0> -> |+>. So RX -> H.
    # RY means prepare |i+>. H |0> -> |+>, S |+> -> |i+>. So RY -> H, S.
    # RZ means prepare |0>. Identity on |0>. So RZ -> (nothing).
    # R means prepare |0> (same as RZ in this context usually, or generic reset).
    
    lines = str(circuit).splitlines()
    new_lines = []
    for line in lines:
        if line.startswith("RX"):
            # Replace RX with H
            targets = line[2:].strip()
            new_lines.append(f"H {targets}")
        elif line.startswith("R ") or line.startswith("RZ"):
            # R or RZ is reset to |0>. Since input is |0>, do nothing.
            pass
        elif line.startswith("RY"):
            targets = line[2:].strip()
            new_lines.append(f"H {targets}")
            new_lines.append(f"S {targets}")
        else:
            new_lines.append(line)
            
    processed_circuit_text = "\n".join(new_lines)
    
    output_path = "data/gemini-3-pro-preview/agent_files/candidate_from_baseline.stim"
    with open(output_path, "w") as f:
        f.write(processed_circuit_text)
        
    print(f"Synthesized circuit saved to {output_path}")
    
except Exception as e:
    print(f"Error: {e}")
