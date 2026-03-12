import stim

def main():
    try:
        with open("target_stabilizers_rq3_new_v3.txt", "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]
        if not stabilizers:
            print("No stabilizers found.")
            return

        print(f"Number of stabilizers: {len(stabilizers)}")
        print(f"Length of first stabilizer: {len(stabilizers[0])}")
        
        with open("baseline_rq3_new_v3.stim", "r") as f:
            baseline = stim.Circuit(f.read())
        print(f"Baseline num_qubits: {baseline.num_qubits}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
