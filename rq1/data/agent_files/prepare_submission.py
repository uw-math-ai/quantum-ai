import json

def prepare_submission():
    with open('target_stabilizers_60.txt', 'r') as f:
        stabs = [line.strip() for line in f if line.strip()]
        
    with open('circuit_attempt.stim', 'r') as f:
        circuit = f.read()
        
    print("STABILIZERS_JSON:")
    print(json.dumps(stabs))
    print("\nCIRCUIT_TEXT:")
    print(circuit)

if __name__ == "__main__":
    prepare_submission()
