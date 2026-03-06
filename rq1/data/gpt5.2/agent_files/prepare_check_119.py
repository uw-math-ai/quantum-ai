import json

def prepare_tool_input():
    # Read circuit
    with open(r'data\gemini-3-pro-preview\agent_files\circuit_119_fixed.stim', 'r') as f:
        circuit = f.read()
        
    # Read stabilizers
    with open(r'data\gemini-3-pro-preview\agent_files\stabilizers_119_fixed.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]
        
    # Create the object for check_stabilizers_tool call
    # The tool takes "circuit" and "stabilizers"
    
    # We can write it to a file, then read it.
    output = {
        'circuit': circuit,
        'stabilizers': stabilizers
    }
    
    print(json.dumps(output))

if __name__ == "__main__":
    prepare_tool_input()
