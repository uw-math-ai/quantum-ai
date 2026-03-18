
import stim

def main():
    try:
        # Load baseline
        with open('baseline_rq3_v4.stim', 'r') as f:
            baseline = stim.Circuit(f.read())
        
        # Load stabilizers
        with open('target_stabilizers_rq3_v4.txt', 'r') as f:
            stabs = [line.strip() for line in f if line.strip()]
        
        print(f"Checking {len(stabs)} stabilizers against baseline...")
        print(f"Stabilizer length: {len(stabs[0])}")
        print(f"Baseline qubits: {baseline.num_qubits}")
        
        tableau = stim.Tableau.from_circuit(baseline)
        
        all_preserved = True
        for i, s_str in enumerate(stabs):
            p = stim.PauliString(s_str)
            out_p = tableau(p)
            if p != out_p:
                print(f"Mismatch at index {i}!")
                print(f"In:  {p}")
                print(f"Out: {out_p}")
                all_preserved = False
                break
        
        if all_preserved:
            print("Baseline preserves all stabilizers identically.")
        else:
            print("Baseline DOES NOT preserve all stabilizers identically.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
