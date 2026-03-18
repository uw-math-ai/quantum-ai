import stim

def main():
    try:
        # Load baseline to get qubit count and stabilizers
        with open("current_task_baseline.stim", "r") as f:
            baseline_text = f.read().strip()
        baseline = stim.Circuit(baseline_text)
        num_qubits = baseline.num_qubits
        print(f"Baseline qubits: {num_qubits}")

        # Extract stabilizers from baseline
        print("Extracting stabilizers from baseline...")
        sim = stim.TableauSimulator()
        sim.do(baseline)
        # canonical_stabilizers returns a list of PauliStrings
        # We use these as the definition of the state
        extracted_stabs = sim.canonical_stabilizers()
        print(f"Extracted {len(extracted_stabs)} stabilizers.")
        
        pauli_strings = extracted_stabs

        try:
            # Use graph_state synthesis
            # allow_redundant=True is not needed for canonical stabilizers (they are independent)
            # but good to have.
            tableau = stim.Tableau.from_stabilizers(pauli_strings, allow_redundant=True, allow_underconstrained=True)
            circuit = tableau.to_circuit(method="graph_state")
            
            # Write to file
            out_file = "candidate.stim"
            with open(out_file, "w") as f:
                f.write(str(circuit))
            print(f"Successfully wrote {out_file}")
            
        except Exception as e:
            print(f"Synthesis failed: {e}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
