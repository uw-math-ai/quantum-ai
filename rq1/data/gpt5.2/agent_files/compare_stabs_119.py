import stim

def compare():
    # Read from file
    with open("stabilizers_119.txt", "r") as f:
        file_lines = [l.strip() for l in f if l.strip()]
        
    # Read from solve_119.py (extract the list)
    # I'll just copy the list here to be sure I'm using what I saw in view
    # Actually, I can import it if I modify solve_119.py to be importable
    # Or I can read solve_119.py and parse it.
    
    with open("solve_119.py", "r") as f:
        content = f.read()
        
    # Extract the list between stabilizers = [ and ]
    start = content.find("stabilizers = [")
    end = content.find("]", start)
    list_str = content[start:end+1]
    # Execute this snippet to get the variable
    exec(list_str)
    # Now I have local variable 'stabilizers'
    
    code_lines = locals()['stabilizers']
    
    print(f"File lines: {len(file_lines)}")
    print(f"Code lines: {len(code_lines)}")
    
    for i in range(min(len(file_lines), len(code_lines))):
        if file_lines[i] != code_lines[i]:
            print(f"Mismatch at index {i}:")
            print(f"File: {file_lines[i]}")
            print(f"Code: {code_lines[i]}")
            
    if len(file_lines) != len(code_lines):
        print("Length mismatch!")

if __name__ == "__main__":
    compare()
