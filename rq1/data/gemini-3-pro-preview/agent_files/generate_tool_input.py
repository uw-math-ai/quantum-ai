import json

def generate_input():
    # Read stabilizers
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_133.txt", "r") as f:
        stabilizers = [l.strip() for l in f if l.strip()]

    # Read circuit
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_133.stim", "r") as f:
        circuit = f.read().strip()

    # Create JSON
    data = {
        "circuit": circuit,
        "stabilizers": stabilizers
    }
    
    # Write to a file so I can view it or print it
    print(json.dumps(data))
        
    print("Tool input generated.")

if __name__ == "__main__":
    generate_input()
