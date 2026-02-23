import json

def generate_tool_input():
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_114.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]
        
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_114_robust.stim', 'r') as f:
        circuit = f.read()
        
    tool_input = {
        "circuit": circuit,
        "stabilizers": stabilizers
    }
    
    # Print only the circuit length to verify, don't print full JSON yet
    print(f"Circuit length: {len(circuit)}")
    
    # Print first 100 chars
    print(circuit[:100])

generate_tool_input()
