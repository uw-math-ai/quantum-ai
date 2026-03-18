import stim
import sys

def synthesize_from_baseline():
    # 1. Load baseline
    try:
        with open("baseline.stim", "r") as f:
            baseline_text = f.read()
        circuit = stim.Circuit(baseline_text)
    except Exception as e:
        print(f"Error loading baseline: {e}")
        return

    # 2. Extract Tableau
    sim = stim.TableauSimulator()
    sim.do(circuit)
    # The circuit prepares a state from |0...0>. 
    # The inverse tableau of the simulator maps the current state back to |0...0>.
    # So the inverse of that (current_inverse_tableau().inverse()) is the tableau that maps |0...0> to the current state.
    tableau = sim.current_inverse_tableau().inverse()

    # 3. Synthesize using graph_state method
    try:
        new_circuit = tableau.to_circuit(method="graph_state")
        
        # Post-process: Remove RX resets (graph state implies initialization to |0> + H)
        # Stim's graph_state output usually looks like:
        # RX 0 1 2 ...
        # CZ ...
        # ...
        # We can replace RX with H if we assume the input is |0>
        # But wait, RX is "Reset X". If we start from |0> (Z basis), we want to go to X basis (+ state).
        # H does |0> -> |+>.
        # RX does (anything) -> |+>.
        # So replacing RX with H is valid if we are sure we start at |0>.
        # However, for safety, let's keep it as is first, or use a regex to replace.
        # But the prompt says "Do NOT introduce measurements, resets".
        # So we MUST replace RX with H.
        
        circuit_str = str(new_circuit)
        # Replace "RX" with "H" (assuming standard Stim output format where RX is used for init)
        # Actually, let's be more careful.
        # graph_state output: "RX 0 1 2" -> "H 0 1 2"
        # Note: RX in stim is a reset to X eigenstate.
        
        # Let's write to file
        with open("candidate.stim", "w") as f:
            f.write(circuit_str.replace("RX", "H"))
            
    except Exception as e:
        print(f"Error synthesizing: {e}")

if __name__ == "__main__":
    synthesize_from_baseline()
