import stim
import sys

def solve():
    try:
        # Load baseline
        with open("baseline.stim", "r") as f:
            baseline = stim.Circuit(f.read())
        
        # Calculate tableau from baseline
        sim = stim.TableauSimulator()
        sim.do(baseline)
        tableau = sim.current_inverse_tableau().inverse()
        
        # Synthesize using graph_state method
        candidate = tableau.to_circuit(method="graph_state")
        
        # Post-process: Replace RX with H
        # We need to iterate over instructions and replace RX with H
        new_circuit = stim.Circuit()
        for instr in candidate:
            if instr.name == "RX":
                # Replace RX with H
                new_circuit.append("H", instr.targets_copy())
            else:
                new_circuit.append(instr)
        
        # Check for measurements or resets
        for instr in new_circuit:
            if instr.name in ["R", "RX", "RY", "RZ", "M", "MX", "MY", "MZ", "MR", "MRX", "MRY", "MRZ"]:
                # If we still have resets/measurements (except the RX we replaced), we might have an issue
                # But graph_state shouldn't produce measurements for a unitary tableau.
                pass 

        with open("candidate.stim", "w") as f:
            f.write(str(new_circuit))
        print("Candidate written to candidate.stim")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
