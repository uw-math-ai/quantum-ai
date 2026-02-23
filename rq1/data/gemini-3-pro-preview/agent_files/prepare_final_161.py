
import json

def prepare():
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_161.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]
        
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_161_v2.stim', 'r') as f:
        circuit = f.read()
        
    data = {
        "circuit": circuit,
        "stabilizers": stabilizers
    }
    
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\final_submission.json', 'w') as f:
        json.dump(data, f)
        
    print("Prepared final_submission.json")

if __name__ == "__main__":
    prepare()
