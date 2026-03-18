import stim
import sys

try:
    # Load baseline circuit
    print("Loading baseline circuit...")
    with open("baseline_rq3_new.stim", "r") as f:
        baseline_str = f.read()
    baseline = stim.Circuit(baseline_str)
    
    # Extract tableau from baseline
    print("Simulating baseline to extract tableau...")
    sim = stim.TableauSimulator()
    sim.do(baseline)
    
    # Get the inverse tableau of the current state.
    # The state is U|0>. The tableau represents U.
    # sim.current_inverse_tableau() gives U^{-1}.
    # So we take the inverse of that to get U (or rather, the tableau of the state).
    # Wait, current_inverse_tableau() returns the tableau T such that T(state) = |0>.
    # So T is U^{-1}.
    # We want to synthesize a circuit for U.
    # So we use T.inverse().
    
    tableau = sim.current_inverse_tableau().inverse()
    
    print("Synthesizing graph state circuit...")
    # Generate circuit using graph_state method
    # This method is usually optimal for CX count (uses CZ)
    circuit = tableau.to_circuit(method="graph_state")
    
    # Check for RX gates and replace with H if necessary
    # (Memory suggests replacing RX with H if starting from |0>)
    circuit_str = str(circuit)
    if "RX" in circuit_str:
         print("Circuit contains RX gates. Replacing with H...")
         circuit_str = circuit_str.replace("RX", "H")
    
    # Check for RZ gates? Graph state usually uses H, S, CZ.
    # Sometimes RZ is used for phases.
    
    # Write to file
    out_file = "candidate_rq3_new.stim"
    with open(out_file, "w") as f:
        f.write(circuit_str)
        
    print(f"Successfully generated {out_file}")
    
except Exception as e:
    print(f"Error generating circuit: {e}")
    sys.exit(1)
