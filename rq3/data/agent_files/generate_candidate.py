import stim
import sys

def generate_circuit():
    try:
        with open("target_stabilizers_76.txt", "r") as f:
            content = f.read().replace(',', '\n')
            lines = [line.strip() for line in content.split('\n') if line.strip()]
    except FileNotFoundError:
        print("Error: target_stabilizers_76.txt not found.")
        return

    # Parse stabilizers
    stabilizers = []
    for line in lines:
        try:
            stabilizers.append(stim.PauliString(line))
        except Exception as e:
            print(f"Error parsing line '{line}': {e}")

    print(f"Loaded {len(stabilizers)} stabilizers.")
    if len(stabilizers) > 0:
        print(f"First stabilizer length: {len(stabilizers[0])}")

    try:
        # allow_underconstrained=True because we just need to preserve THESE
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        print(f"Successfully created tableau with {len(tableau)} qubits.")
        
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Try graph state synthesis
    try:
        circuit = tableau.to_circuit(method="graph_state")
        
        cleaned_circuit = stim.Circuit()
        for instr in circuit:
            if instr.name == "RX":
                cleaned_circuit.append("H", instr.targets_copy())
            elif instr.name == "R" or instr.name == "RZ":
                pass 
            elif instr.name == "MY" or instr.name == "MZ" or instr.name == "MX":
                 cleaned_circuit.append(instr)
            else:
                cleaned_circuit.append(instr)
        
        # print("CANDIDATE_START")
        # print(cleaned_circuit)
        # print("CANDIDATE_END")
        
        # Verify using Simulator
        sim = stim.TableauSimulator()
        sim.do(cleaned_circuit)
        
        valid = True
        failed_count = 0
        for i, s in enumerate(stabilizers):
             val = sim.peek_observable_expectation(s)
             if val != 1:
                 # print(f"Stabilizer {i} not preserved (val={val})")
                 failed_count += 1
                 valid = False
        
        if valid:
            print("VERIFICATION SUCCESS: All stabilizers preserved.")
            # Write to file
            with open("candidate.stim", "w") as f:
                f.write(str(cleaned_circuit))
            print("Wrote candidate to candidate.stim")
        else:
            print(f"VERIFICATION FAILED: {failed_count} stabilizers not preserved.")

    except Exception as e:
        print(f"Error during synthesis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_circuit()
