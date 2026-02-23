import stim

def check():
    print("Loading stabilizers...")
    try:
        with open("data/gemini-3-pro-preview/agent_files/stabilizers_72.txt", "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error loading stabilizers: {e}")
        return

    print(f"Loaded {len(stabilizers)} stabilizers")
    
    print("Loading circuit...")
    try:
        with open("circuit_72.stim", "r") as f:
            circuit_text = f.read()
    except Exception as e:
        print(f"Error loading circuit: {e}")
        return
    
    try:
        c = stim.Circuit(circuit_text)
        print(f"Loaded circuit with {c.num_qubits} qubits")
    except Exception as e:
        print(f"Error parsing circuit: {e}")
        return

    print("Simulating...")
    s = stim.TableauSimulator()
    s.do_circuit(c)
    
    preserved = 0
    for i, stab_str in enumerate(stabilizers):
        try:
            p = stim.PauliString(stab_str)
            # peek_observable_expectation returns +1, -1, or 0
            exp = s.peek_observable_expectation(p)
            if exp == 1:
                preserved += 1
            elif i < 5:
                print(f"Stabilizer {i} not preserved. Expectation: {exp}")
                print(f"Stab: {stab_str}")
        except Exception as e:
            print(f"Error checking stabilizer {i}: {e}")

    print(f"Preserved: {preserved}/{len(stabilizers)}")

if __name__ == "__main__":
    check()
