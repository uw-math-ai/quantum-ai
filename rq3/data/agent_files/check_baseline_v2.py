import stim
import sys

def robust_load_stabilizers(filename):
    with open(filename, 'r') as f:
        text = f.read()
    # Remove all whitespace
    clean_text = "".join(text.split())
    
    # Guess length N
    N = 153
    if len(clean_text) % N != 0:
        print(f"Warning: Clean text length {len(clean_text)} is not multiple of {N}.")
        # Check if 152 works
        if len(clean_text) % 152 == 0:
            N = 152
            print("Using N=152")
        else:
            print(f"Using N={N} anyway (will truncate or pad end)")
            
    stabs = [clean_text[i:i+N] for i in range(0, len(clean_text), N)]
    # Filter out short ones at end
    if len(stabs[-1]) != N:
        stabs.pop()
        
    return stabs

def check():
    print("Fixing stabilizers...")
    target_stabs = robust_load_stabilizers("unique_stabilizers.txt")
    print(f"Loaded {len(target_stabs)} stabilizers of length {len(target_stabs[0]) if target_stabs else 0}")
    
    # Save fixed
    with open("fixed_stabilizers.txt", "w") as f:
        for s in target_stabs:
            f.write(s + "\n")
            
    consistent = False
    try:
        stim_stabs = [stim.PauliString(s) for s in target_stabs]
        _ = stim.Tableau.from_stabilizers(stim_stabs, allow_underconstrained=True)
        print("Target stabilizers are CONSISTENT.")
        consistent = True
    except Exception as e:
        print(f"Target stabilizers are INCONSISTENT: {e}")

    print("\nChecking baseline circuit...")
    with open("unique_baseline.stim", "r") as f:
        base_text = f.read()
    
    base_circ = stim.Circuit(base_text)
    sim = stim.TableauSimulator()
    sim.do(base_circ)
    
    fails = 0
    for i, s in enumerate(target_stabs):
        if len(s) != base_circ.num_qubits:
             # Handle mismatch
             pass
        # Truncate or pad s to match num_qubits for check
        s_check = s
        if len(s) > base_circ.num_qubits:
            s_check = s[:base_circ.num_qubits]
        elif len(s) < base_circ.num_qubits:
            s_check = s + "I" * (base_circ.num_qubits - len(s))
            
        if sim.peek_observable_expectation(stim.PauliString(s_check)) != 1:
            fails += 1
            
    print(f"Baseline fails {fails}/{len(target_stabs)} target stabilizers.")
    
    print("\nComputing stabilizers of baseline...")
    base_stabs = sim.canonical_stabilizers()
    print(f"Baseline has {len(base_stabs)} canonical stabilizers.")
    
    # Check if baseline stabilizers are consistent (they must be)
    # Also check if baseline stabilizers imply target stabilizers?
    # If baseline fails targets, then they are different states.
    
    if not consistent:
        print("Since targets are inconsistent, using BASELINE stabilizers as truth.")
        with open("fixed_stabilizers.txt", "w") as f:
            for s in base_stabs:
                f.write(str(s) + "\n")
    elif fails > 0:
        print("Target consistent but baseline fails. Trusting TARGET.")
        # But wait, if baseline fails, it means the baseline circuit is 'wrong' for the target?
        # But task says "improve baseline while preserving same stabilizer behavior".
        # This implies "preserve the behavior OF THE BASELINE".
        # If prompt targets != baseline behavior, which one to pick?
        # "Target stabilizers (must all be preserved): ..." -> Explicit instruction.
        # "preserving the same stabilizer behavior" -> usually means "preserving the stabilizers of the state".
        # If prompt targets are consistent, I must use them.
        # If baseline fails them, then baseline is invalid w.r.t targets.
        # So I must find a circuit that satisfies TARGETS.
        pass
    else:
        print("Target consistent and baseline matches.")

if __name__ == "__main__":
    check()
