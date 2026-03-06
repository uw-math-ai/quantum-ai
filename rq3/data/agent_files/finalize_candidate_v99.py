import stim
import re
import sys

def main():
    # Load candidate
    with open("candidate.stim", "r") as f:
        content = f.read()
    
    circuit = stim.Circuit(content)
    new_circuit = stim.Circuit()

    for instr in circuit:
        if instr.name == "RX":
            # Replace RX with H (assuming input |0>)
            # RX resets to |+>. From |0>, H goes to |+>.
            targets = instr.targets_copy()
            new_circuit.append("H", targets)
        elif instr.name == "R" or instr.name == "RZ":
            pass
        elif instr.name == "RY":
             targets = instr.targets_copy()
             new_circuit.append("H", targets)
             new_circuit.append("S", targets)
        elif instr.name == "TICK":
            pass
        else:
            new_circuit.append(instr)

    # Load stabilizers
    try:
        with open("target_stabilizers.txt", "r") as f:
            stab_content = f.read()
        stabs = re.findall(r'[IXYZ]+', stab_content)
        stabs = [s for s in stabs if len(s) > 10]
        print(f"Loaded {len(stabs)} stabilizers.")

        sim = stim.TableauSimulator()
        sim.do_circuit(new_circuit)
        
        valid = True
        failed_count = 0
        for i, s in enumerate(stabs):
            try:
                pauli = stim.PauliString(s)
                if sim.peek_observable_expectation(pauli) != 1:
                    if failed_count < 5:
                        print(f"Stabilizer {i} failed.")
                    valid = False
                    failed_count += 1
            except Exception as e:
                print(f"Error checking stabilizer {i}: {e}")
                valid = False
                failed_count += 1
        
        if valid:
            print("Final circuit is valid.")
            with open("candidate_final.stim", "w") as f:
                f.write(str(new_circuit))
        else:
            print(f"Final circuit failed validation. {failed_count} failures.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
