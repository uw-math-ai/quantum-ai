import stim
import sys

def verify():
    # Load stabilizers
    with open("data/gemini-3-pro-preview/agent_files/stabilizers_133.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    # Load circuit
    with open("data/gemini-3-pro-preview/agent_files/circuit_133_v2.stim", "r") as f:
        circuit_lines = f.readlines()
    
    # Clean header if present
    cleaned_lines = []
    for line in circuit_lines:
        if line.startswith("#") or not line.strip():
            continue
        cleaned_lines.append(line)
        
    circuit_text = "".join(cleaned_lines)
    try:
        circuit = stim.Circuit(circuit_text)
    except Exception as e:
        print(f"Error parsing circuit: {e}")
        return

    sim = stim.TableauSimulator()
    sim.do_circuit(circuit)
    
    t_inv = sim.current_inverse_tableau()
    
    failed = 0
    total = len(stabilizers)
    
    for i, s in enumerate(stabilizers):
        p = stim.PauliString(s)
        out = t_inv(p)
        # Check if out is +Z or -Z (pure Z string)
        # Specifically, must be +1 eigenstate of |0>, so +Z_i...Z_j...
        
        # Check for non-Z components (X or Y)
        # In stim, X and Z are stored as bits. X bit set -> X or Y.
        # So check if any X bit is set.
        
        # Also check sign.
        if out.sign != +1:
             # It could be -1? No, stabilizers of |0> have +1.
             # If -1, it means -Z which stabilizes |1>. But we start at |0>.
             pass
        
        # Wait, how do I check for Z-only?
        # Use explicit check.
        
        is_z = True
        # Inspect string representation
        s_out = str(out)
        if 'X' in s_out or 'Y' in s_out:
            is_z = False
            
        if not is_z or out.sign == -1:
            failed += 1
            if failed <= 1:
                print(f"Failed {i}: {s}")
                print(f"Result: {out}")
                
    print(f"Failed: {failed}/{total}")

if __name__ == "__main__":
    verify()
