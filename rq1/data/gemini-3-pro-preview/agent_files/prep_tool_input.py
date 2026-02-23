def get_stabs_for_tool():
    path = r'data\gemini-3-pro-preview\agent_files\stabilizers_fixed_final.txt'
    with open(path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    indices = [0, 34, 43, 51, 109, 152]
    selected = [lines[i] for i in indices]
    
    # Also print the circuit content to a file so I can copy it easily if needed?
    # No, I just need the text.
    
    print("STABILIZERS_FOR_TOOL")
    print(selected)

if __name__ == "__main__":
    get_stabs_for_tool()
