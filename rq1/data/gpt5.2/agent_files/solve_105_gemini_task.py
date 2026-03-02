import stim
import sys

def solve():
    try:
        with open("data/gemini-3-pro-preview/agent_files/stabilizers.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Stabilizers file not found.")
        return

    print(f"Loaded {len(lines)} lines.")
    
    # Analyze lengths
    target_length = 105
    cleaned_stabilizers = []
    
    for i, line in enumerate(lines):
        if len(line) == target_length:
            cleaned_stabilizers.append(line)
        elif len(line) > target_length:
            print(f"Trimming line {i+1}: '{line}' -> {line[:target_length]}")
            cleaned_stabilizers.append(line[:target_length])
        else:
            print(f"Skipping short line {i+1}: '{line}'")
            # Maybe pad?
            # cleaned_stabilizers.append(line + "I"*(target_length-len(line)))
            pass

    # Convert to PauliStrings
    stabilizers = [stim.PauliString(s) for s in cleaned_stabilizers]
    print(f"Converted {len(stabilizers)} stabilizers to PauliStrings.")

    try:
        # Check for consistency
        # stim.Tableau.from_stabilizers will fail if inconsistent
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        print("Successfully created tableau from stabilizers.")
        
        circuit = tableau.to_circuit()
        # Ensure measurements or something? No, just state prep.
        
        with open("data/gemini-3-pro-preview/agent_files/circuit.stim", "w") as f:
            f.write(str(circuit))
        print("Circuit saved to circuit.stim")
        
    except Exception as e:
        print(f"Error creating tableau: {e}")
        # If inconsistent, we need to find the conflicting ones
        pass

if __name__ == "__main__":
    solve()
