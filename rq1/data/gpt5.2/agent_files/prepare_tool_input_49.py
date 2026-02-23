import json

def main():
    circuit_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_49_gemini.stim"
    stabs_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_49.txt"
    
    with open(circuit_path, "r") as f:
        circuit = f.read()
    
    with open(stabs_path, "r") as f:
        stabs = [line.strip() for line in f if line.strip()]
        
    data = {
        "circuit": circuit,
        "stabilizers": stabs
    }
    
    # Print the JSON, but we can't just pass this to the tool directly via python.
    # We have to make the tool call ourselves.
    # So I will just print the stabilizers list formatted for the tool call.
    print(json.dumps(stabs))

if __name__ == "__main__":
    main()
