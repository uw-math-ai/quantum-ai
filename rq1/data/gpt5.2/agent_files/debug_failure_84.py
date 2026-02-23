import stim

def debug_failure():
    # Failed stabilizer
    failed_z = stim.PauliString("IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIII")
    
    # Load all stabilizers
    with open("stabilizers_84_fixed.txt", "r") as f:
        stabs = [stim.PauliString(line.strip()) for line in f if line.strip()]
        
    print(f"Failed Z: {failed_z}")
    
    # Check commutativity with all others
    for i, s in enumerate(stabs):
        if not failed_z.commutes(s):
            print(f"Anticommutes with index {i}: {s}")

if __name__ == "__main__":
    debug_failure()
