import stim
import sys

def analyze():
    print("Loading baseline...")
    with open("my_baseline_v2.stim", "r") as f:
        baseline_text = f.read()
    circuit = stim.Circuit(baseline_text)
    
    print(f"Baseline gates: {len(circuit)}")
    cx_count = 0
    for instr in circuit:
        if instr.name == "CX" or instr.name == "CNOT":
            cx_count += len(instr.targets_copy()) // 2
    print(f"Baseline CX count: {cx_count}")
    
    print("Loading stabilizers...")
    with open("my_stabilizers_corrected.txt", "r") as f:
        lines = [l.strip().replace(',', '') for l in f.readlines() if l.strip()]
    
    stabilizers = []
    for l in lines:
        try:
            stabilizers.append(stim.PauliString(l))
        except:
            print(f"Skipping invalid line: {l}")
    
    print(f"Number of stabilizers: {len(stabilizers)}")
    if len(stabilizers) > 0:
        num_qubits = len(stabilizers[0])
        print(f"Number of qubits: {num_qubits}")
    else:
        print("No stabilizers found")
        return
    
    # Check commutativity
    print("Checking commutativity...")
    all_commute = True
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if not stabilizers[i].commutes(stabilizers[j]):
                print(f"Stabilizers {i} and {j} anti-commute!")
                all_commute = False
                # break # Don't break, see how many
        # if not all_commute: break
            
    if all_commute:
        print("All stabilizers commute.")
    else:
        print("Stabilizers do NOT all commute.")

    # Check if baseline preserves them
    print("Checking preservation...")
    sim = stim.TableauSimulator()
    sim.do_circuit(circuit)
    
    preserved_count = 0
    for s in stabilizers:
        if sim.peek_observable_expectation(s) == 1:
            preserved_count += 1
        else:
            print(f"Failed to preserve: {s} (Exp: {sim.peek_observable_expectation(s)})")
            
    print(f"Preserved {preserved_count}/{len(stabilizers)}")
    
    # Try to synthesize
    if all_commute:
        print("Attempting synthesis from stabilizers (FORCED)...")
        try:
            # allow_underconstrained=True is important if we have fewer stabilizers than qubits or if they are dependent
            tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
            
            # Method 1: Elimination
            synth_circuit = tableau.to_circuit(method="elimination")
            cx = sum(1 for i in synth_circuit if i.name == "CX" or i.name == "CNOT")
            print(f"Synthesized (elimination) CX count: {cx}")
            
            # Method 2: Graph State
            synth_circuit_graph = tableau.to_circuit(method="graph_state")
            cx_graph = sum(1 for i in synth_circuit_graph if i.name == "CX" or i.name == "CNOT")
            cz_graph = sum(1 for i in synth_circuit_graph if i.name == "CZ")
            print(f"Synthesized (graph_state) CX count: {cx_graph}, CZ count: {cz_graph}")
            
            # Save graph state candidate
            with open("my_candidate_v3.stim", "w") as f:
                # Replace RX with H for initialization from |0>
                # But wait, RX resets to |+>. H on |0> prepares |+>.
                # So replacing RX with H is correct IF the circuit starts at |0>.
                # However, stim's graph state circuit starts with RX.
                # We should strip RX and assume |0> input, then add H on all used qubits?
                # The graph state circuit structure is: RX (reset to +), CZs, Local Cliffords.
                # If we remove RX, we have |0>. We need |+>. So we need H on all qubits.
                # Let's just do textual replacement.
                
                # Also, we need to handle the case where RX is not on all qubits.
                # But typically it is.
                
                circ_str = str(synth_circuit_graph)
                lines = circ_str.splitlines()
                new_lines = []
                for line in lines:
                    if line.startswith("RX"):
                        # Replace RX with H
                        new_lines.append(line.replace("RX", "H"))
                    elif line.startswith("TICK"):
                        continue
                    else:
                        new_lines.append(line)
                
                final_circ = "\n".join(new_lines)
                f.write(final_circ)
                print(f"Wrote candidate to my_candidate_v3.stim")
                
        except Exception as e:
            print(f"Synthesis failed: {e}")

if __name__ == "__main__":
    analyze()
