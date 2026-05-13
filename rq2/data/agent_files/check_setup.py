import sys
import stim

def parse_stim(path):
    with open(path, 'r') as f:
        return f.read().strip()

def get_stabilizers(path):
    with open(path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

if __name__ == "__main__":
    circuit = parse_stim("circuit_input.stim")
    stabilizers = get_stabilizers("stabilizers.txt")
    
    # We will use the validate_circuit tool in the next turn.
    # This script is just to verify we can read them and maybe print some info.
    print(f"Circuit length: {len(circuit)}")
    print(f"Num stabilizers: {len(stabilizers)}")
