import stim
import sys

def count_cx(circuit):
    count = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT"]:
            count += len(instr.targets_copy()) // 2
    return count

def compute_volume(circuit):
    return sum(1 for _ in circuit.flattened())

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
        circuit = stim.Circuit.from_file("my_baseline.stim")
        stabilizers = load_stabilizers("my_stabilizers.txt")
        
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

        # Analyze structure
        # Check if we can synthesize better
        # Strategy 1: Tableau Synthesis
        try:
            tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
            synth_circuit = tableau.to_circuit("elimination")
            cx_synth = count_cx(synth_circuit)
            vol_synth = compute_volume(synth_circuit)
            print(f"Synthesis (elimination): CX={cx_synth}, Volume={vol_synth}")
            
            # Check if synthesis is valid
            p, f = verify_stabilizers(synth_circuit, stabilizers)
            if not f:
                print("Synthesis is VALID.")
            else:
                print("Synthesis is INVALID.")
                
            if cx_synth < cx:
                 print("Synthesis is BETTER.")
                 with open("candidate_elimination.stim", "w") as f:
                     f.write(str(synth_circuit))
            
            # Graph State Synthesis
            # This requires converting the tableau to a graph state form if possible
            # stim doesn't have direct graph state synthesis, but we can try other methods
            
        except Exception as e:
            print(f"Synthesis failed: {e}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
