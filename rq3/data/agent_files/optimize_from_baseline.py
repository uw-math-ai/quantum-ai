import stim

def main():
    try:
        with open("current_baseline.stim", "r") as f:
            baseline_text = f.read()
            baseline = stim.Circuit(baseline_text)

        # Get the tableau of the state prepared by baseline (assuming input |0>)
        t = stim.Tableau.from_circuit(baseline)

        # Synthesize new circuit using graph_state method
        new_circuit = t.to_circuit(method="graph_state")
        
        # Print lines, excluding RX and TICK
        for line in str(new_circuit).splitlines():
            if line.strip().startswith("RX") or line.strip().startswith("TICK"):
                continue
            print(line)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()