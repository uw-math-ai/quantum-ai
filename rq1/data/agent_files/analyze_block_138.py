import sys

# Ranges based on analysis
# Shift is 23.
# Block 0: 0-22

# Let's extract the stabilizers for block 0.
# We look for stabilizers that are fully contained in 0-22.
# And maybe some that connect blocks?

def get_block_stabilizers():
    with open("target_stabilizers_138.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    block_0_stabs = []
    global_stabs = []
    
    for i, s in enumerate(lines):
        support = [j for j, c in enumerate(s) if c != 'I']
        if not support: continue
        
        if max(support) < 23:
            block_0_stabs.append(s[0:23])
        elif min(support) >= 23:
            # Check if it's a shift of a block 0 stab
            # We assume it is for now, just ignore
            pass
        else:
            # Cross-block stabilizer?
            global_stabs.append((i, s))

    print("Block 0 stabilizers (restricted to first 23 qubits):")
    for s in block_0_stabs:
        print(s)

    print("\nGlobal stabilizers:")
    for i, s in global_stabs:
        print(f"Index {i}: {s}")

if __name__ == "__main__":
    get_block_stabilizers()
