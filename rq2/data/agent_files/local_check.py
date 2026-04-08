import stim
import sys

def check_stabilizers(circuit_str, stabilizers):
    circuit = stim.Circuit(circuit_str)
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    satisfied = []
    for stab in stabilizers:
        stab = stab.strip()
        if not stab: continue
        # Convert string like "XXXX..." to stim.PauliString
        try:
            p = stim.PauliString(stab)
        except Exception as e:
            print(f"Error parsing stabilizer '{stab}': {e}")
            continue
            
        # Check if the stabilizer is stabilized
        # We can check this by seeing if the expectation value is +1
        # peek_observable_expectation returns +1, -1, or 0 (if random)
        val = sim.peek_observable_expectation(p)
        if val != 1:
            satisfied.append(False)
            print(f"Failed stabilizer: {stab} (Expectation: {val})")
        else:
            satisfied.append(True)
        
    return all(satisfied), satisfied

def analyze_faults(circuit_str, data_qubits, distance):
    # This is a local approximation of the validate_circuit tool logic
    # just to give us an idea.
    # The real validation is done by the tool.
    pass

if __name__ == "__main__":
    with open("circuit_input.stim", "r") as f:
        circuit_str = f.read()
    
    with open("stabilizers_input.txt", "r") as f:
        stabilizers = f.readlines()
        
    all_good, satisfied = check_stabilizers(circuit_str, stabilizers)
    print(f"Stabilizers preserved: {all_good}")
    if not all_good:
        print(f"Satisfied {sum(satisfied)}/{len(satisfied)}")
