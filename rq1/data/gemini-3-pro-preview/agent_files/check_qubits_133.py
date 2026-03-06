import re

def check_max_qubit():
    with open("data/gemini-3-pro-preview/agent_files/circuit_133_cleaned.stim", "r") as f:
        content = f.read()
    
    # Simple regex to find integers
    # Be careful not to match instruction names or non-qubit args if any
    # Stim format is mostly simple: INST q1 q2 ...
    ints = [int(s) for s in re.findall(r'\b\d+\b', content)]
    if ints:
        print(f"Max qubit index: {max(ints)}")
        print(f"Num qubits needed: {max(ints) + 1}")
    else:
        print("No qubits found")

if __name__ == "__main__":
    check_max_qubit()
