import stim

def check():
    with open("stabilizers_171.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    print(f"Number of stabilizers: {len(stabilizers)}")
    print(f"Number of qubits: {len(stabilizers[0])}")

    try:
        # Check if they commute
        t = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in stabilizers])
        print("Stabilizers are consistent and commuting.")
    except Exception as e:
        print(f"Issue with stabilizers: {e}")

if __name__ == "__main__":
    check()
