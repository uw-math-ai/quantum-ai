import stim
import sys

def debug():
    # The failing stabilizer reported by the tool
    failing_stab_str = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIII"
    print(f"Checking failing stabilizer (len {len(failing_stab_str)}): {failing_stab_str}")
    
    # Load the circuit
    circ_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_105.stim"
    with open(circ_path, "r") as f:
        circuit_text = f.read()
    circuit = stim.Circuit(circuit_text)
    
    # Simulate
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    s = stim.PauliString(failing_stab_str)
    ev = sim.peek_observable_expectation(s)
    print(f"Expectation value: {ev}")
    
    # Also check if it's in the file
    stab_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_105.txt"
    with open(stab_path, "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    if failing_stab_str in lines:
        print("Stabilizer IS in the file.")
    else:
        print("Stabilizer IS NOT in the file.")
        # Print close matches
        for l in lines:
            if "XXXX" in l and l.endswith("IIIIIII"):
                 print(f"Found close match: {l}")

if __name__ == "__main__":
    debug()
