import stim

def verify():
    print("Loading circuit...")
    try:
        with open("circuit_186_final.stim", "r") as f:
            circuit = stim.Circuit(f.read())
    except Exception as e:
        print(f"Error loading circuit: {e}")
        return

    print("Loading stabilizers...")
    with open("stabilizers_186.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    # Fix S105
    if len(lines[105]) == 184:
        lines[105] = "II" + lines[105]
    
    stabilizers = [stim.PauliString(line) for line in lines]
    
    print(f"Verifying {len(stabilizers)} stabilizers...")
    
    # Simulate
    # Note: tableau.from_circuit() is efficient for Cliffords
    try:
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        failures = 0
        for i, s in enumerate(stabilizers):
            # measure_observable returns True if -1, False if +1
            # We want +1 eigenstate => False (0)
            if sim.measure_observable(s):
                print(f"FAIL: Stabilizer {i} not satisfied.")
                failures += 1
                if failures >= 5:
                    print("Stopping after 5 failures.")
                    break
        
        if failures == 0:
            print("SUCCESS: All stabilizers verified.")
        else:
            print(f"FAILURE: {failures} stabilizers failed.")
            
    except Exception as e:
        print(f"Simulation error: {e}")

if __name__ == "__main__":
    verify()
