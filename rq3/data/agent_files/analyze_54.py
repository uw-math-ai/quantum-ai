import stim
import sys

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT"]:
            count += len(instr.targets_copy()) // 2
    return count

def compute_volume(circuit):
    # Volume: total gate count in volume gate set (CX, CY, CZ, H, S, SQRT_X, etc.)
    # We should count each operation. 
    # E.g. H 0 1 2 is 3 gates.
    count = 0
    for instr in circuit:
        # Check if it is a gate
        if instr.name in ["H", "S", "CX", "CY", "CZ", "SQRT_X", "SQRT_Y", "SQRT_Z", "X", "Y", "Z", "CNOT"]:
            # Count targets. For 2-qubit gates, 2 targets = 1 gate?
            # Usually volume counts the number of gates.
            # CX 0 1 is 1 gate.
            # H 0 is 1 gate.
            # H 0 1 is 2 gates.
            
            n_args = len(instr.targets_copy())
            if instr.name in ["CX", "CY", "CZ", "CNOT"]:
                count += n_args // 2
            else:
                count += n_args
    return count

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    return [stim.PauliString(l) for l in lines]

def verify_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    preserved = []
    failed = []
    for i, stab in enumerate(stabilizers):
        if sim.peek_observable_expectation(stab) == 1:
            preserved.append(i)
        else:
            failed.append(i)
    return preserved, failed

def main():
    try:
        circuit = stim.Circuit.from_file("baseline_54.stim")
        stabilizers = load_stabilizers("stabilizers_54.txt")
        
        print(f"Loaded circuit with {len(circuit)} instructions.")
        print(f"Loaded {len(stabilizers)} stabilizers.")
        
        cx = count_cx(circuit)
        vol = compute_volume(circuit)
        print(f"Baseline Metrics: CX={cx}, Volume={vol}")
        
        preserved, failed = verify_stabilizers(circuit, stabilizers)
        if not failed:
            print("Baseline is VALID.")
        else:
            print(f"Baseline is INVALID. Failed: {len(failed)}")

        # Try Synthesis
        print("Attempting Tableau Synthesis...")
        try:
            # allow_redundant=True for dependent stabilizers
            tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
            synth_circuit = tableau.to_circuit("elimination")
            
            cx_synth = count_cx(synth_circuit)
            vol_synth = compute_volume(synth_circuit)
            print(f"Synthesis (elimination): CX={cx_synth}, Volume={vol_synth}")
            
            p, f = verify_stabilizers(synth_circuit, stabilizers)
            if not f:
                print("Synthesis is VALID.")
                if cx_synth < cx or (cx_synth == cx and vol_synth < vol):
                    print("Synthesis is BETTER.")
                    with open("candidate_opt.stim", "w") as f:
                        f.write(str(synth_circuit))
                else:
                    print("Synthesis is NOT better.")
            else:
                print("Synthesis is INVALID.")
                
            # Try Graph State Synthesis (simulated by graph_state method of tableau?)
            # stim doesn't expose graph state directly but we can try other heuristic
            
        except Exception as e:
            print(f"Synthesis failed: {e}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
