import stim

def main():
    with open("best_candidate.stim", "r") as f:
        content = f.read()
    
    c = stim.Circuit(content)
    
    with open("stabilizers.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]
    
    sim = stim.TableauSimulator()
    sim.do(c)
    
    failed = []
    for s in stabs:
        if not sim.peek_observable_expectation(stim.PauliString(s)) == 1:
            failed.append(s)
            
    if failed:
        print(f"Raw candidate FAILED to preserve {len(failed)} stabilizers.")
        print(f"Example failure: {failed[0]}")
    else:
        print("Raw candidate PRESERVES all stabilizers.")

if __name__ == "__main__":
    main()
