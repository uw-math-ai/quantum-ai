import os

def analyze():
    print("Reading stabilizers...")
    file_path = r"data\gemini-3-pro-preview\agent_files\stabilizers_152.txt"
    with open(file_path, "r") as f:
        stabilizers = [line.strip() for line in f.readlines() if line.strip()]

    print(f"Number of stabilizers: {len(stabilizers)}")
    if not stabilizers:
        print("No stabilizers found.")
        return

    num_qubits = 152
    print(f"Expected number of qubits: {num_qubits}")
    
    # Check consistency of lengths
    for i, s in enumerate(stabilizers):
        if len(s) != num_qubits:
            print(f"Stabilizer {i} has length {len(s)}")
            print(repr(s))

if __name__ == "__main__":
    analyze()
