import json

def prepare():
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers.txt', 'r') as f:
        stabs = [line.strip() for line in f if line.strip()]
    
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_fixed.stim', 'r') as f:
        circuit = f.read()
        
    data = {
        'circuit': circuit,
        'stabilizers': stabs
    }
    
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\tool_input.json', 'w') as f:
        json.dump(data, f)
        
if __name__ == "__main__":
    prepare()
