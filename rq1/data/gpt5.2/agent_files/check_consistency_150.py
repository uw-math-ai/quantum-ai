import stim

def check_consistency():
    # Read stabilizers
    filename = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_150_v2.txt"
    try:
        with open(filename, "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return

    # Convert to PauliString
    paulis = [stim.PauliString(s) for s in stabilizers]
    
    # Check for anticommutativity
    inconsistent = False
    for i in range(len(paulis)):
        for j in range(i + 1, len(paulis)):
            if not paulis[i].commutes(paulis[j]):
                print(f"Stabilizer {i} anticommutes with Stabilizer {j}")
                # print(f"{stabilizers[i]}")
                # print(f"{stabilizers[j]}")
                inconsistent = True
                
    if not inconsistent:
        print("All stabilizers commute.")
    else:
        print("Found inconsistent stabilizers.")
        
    # Check specifically for the failing ones
    failing_strs = [
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIIXXIIIIIIIIIIIIIIIIIIIIIIIIIII",
        "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIIIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"
    ]
    
    for fs in failing_strs:
        found = False
        for i, s in enumerate(stabilizers):
            if s == fs:
                print(f"Failing stabilizer found at index {i}: {s}")
                found = True
                break
        if not found:
            print(f"Failing stabilizer NOT found in list: {fs}")

if __name__ == "__main__":
    check_consistency()
