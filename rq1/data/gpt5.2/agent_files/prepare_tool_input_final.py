import json

def main():
    circuit_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_49_gemini.stim"
    stabs_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_49.txt"
    
    with open(circuit_path, "r") as f:
        # Read and ensure valid stim format (no extra newlines/artifacts)
        # We can strip, but stim allows newlines.
        circuit = f.read().strip()
    
    with open(stabs_path, "r") as f:
        stabs = [line.strip() for line in f if line.strip()]

    # We can't actually invoke the tool from python.
    # But we can print the JSON payload.
    # However, the user (me) has to paste it into the tool call.
    # The tool call format is not raw JSON, it's specific arguments.
    # So I will just print the stabilizers list as a single line JSON array.
    
    print("STABILIZERS_START")
    print(json.dumps(stabs))
    print("STABILIZERS_END")
    
    # Also print the circuit as a single string (with \n escaped if needed for JSON, but for tool call we pass literal string)
    # The tool call in the chat interface takes a string with newlines.
    # I will just print the circuit content again to be sure.
    print("CIRCUIT_START")
    print(circuit)
    print("CIRCUIT_END")

if __name__ == "__main__":
    main()
