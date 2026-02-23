import json

def prepare_input():
    with open('stabilizers_148.txt', 'r') as f:
        stabs = [line.strip() for line in f if line.strip()]
        
    with open('circuit_generated.stim', 'r') as f:
        circuit = f.read()
        
    data = {
        "circuit": circuit,
        "stabilizers": stabs
    }
    
    with open('tool_input_148.json', 'w') as f:
        json.dump(data, f)
        
prepare_input()
