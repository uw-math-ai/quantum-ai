import json

def generate_tool_input():
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_114.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]
        
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_114.stim', 'r') as f:
        circuit = f.read()
        
    tool_input = {
        "circuit": circuit,
        "stabilizers": stabilizers
    }
    
    print(json.dumps(tool_input))

generate_tool_input()
