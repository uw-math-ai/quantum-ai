import json

def prepare():
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_108.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]
    
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_108.stim', 'r') as f:
        circuit = f.read()

    tool_input = {
        "circuit": circuit,
        "stabilizers": stabilizers
    }
    
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\tool_input_108.json', 'w') as f:
        json.dump(tool_input, f, indent=2)

if __name__ == "__main__":
    prepare()
