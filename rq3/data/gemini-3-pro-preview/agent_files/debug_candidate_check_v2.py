import stim

def debug_check():
    try:
        with open('candidate.stim', 'r') as f:
            cand_text = f.read()
    except FileNotFoundError:
        print("candidate.stim not found")
        return

    try:
        c = stim.Circuit(cand_text)
    except Exception as e:
        print(f"Error parsing candidate.stim: {e}")
        return

    try:
        with open('target_stabilizers.txt', 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        stabs = [stim.PauliString(line) for line in lines]
    except FileNotFoundError:
        print("target_stabilizers.txt not found")
        return
        
    sim = stim.TableauSimulator()
    sim.do(c)
    
    preserved = 0
    total = len(stabs)
    
    # print(f"Checking {total} stabilizers...")
    for i, s in enumerate(stabs):
        # We assume the circuit uses the same qubits as stabilizers (0-62)
        # If circuit uses fewer, Stim pads with I.
        res = sim.measure_observable(s)
        if res: # True/1 means result is -1 (failure)
            print(f"Stab {i}: FAIL") # {s}
        else:
            preserved += 1
            # print(f"Stab {i}: PASS")
            
    print(f"Preserved: {preserved}/{total}")

if __name__ == "__main__":
    debug_check()
