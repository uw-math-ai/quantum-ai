import subprocess
import stim
import sys
import os

def generate_and_process():
    # Run the generation script and capture output
    try:
        result = subprocess.run([sys.executable, 'gen_candidate_graph_state_v4.py'], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print("Generation failed:", e.stderr)
        sys.exit(1)
        
    circuit_text = result.stdout
    
    # Parse the circuit
    try:
        c = stim.Circuit(circuit_text)
    except Exception as e:
        print(f"Error parsing generated circuit: {e}")
        sys.exit(1)

    new_c = stim.Circuit()
    
    for instruction in c:
        if instruction.name == "RX":
            # Replace RX targets with H targets
            # RX resets to |+>. Since input is |0>, H does the same.
            targets = instruction.targets_copy()
            new_c.append("H", targets)
        elif instruction.name == "TICK":
            # Remove TICKs
            pass
        else:
            new_c.append(instruction)
            
    # Save to candidate.stim
    with open('candidate.stim', 'w') as f:
        f.write(str(new_c))
        
    print("Candidate generated and saved to candidate.stim")

if __name__ == "__main__":
    generate_and_process()
