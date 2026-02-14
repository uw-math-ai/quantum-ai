import numpy as np

def parse_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    return lines

stabs = parse_stabilizers('stabilizers_75.txt')
n = len(stabs[0])
print(f"Number of qubits: {n}")
print(f"Number of stabilizers: {len(stabs)}")

# Analyze blocks of 5
num_blocks = n // 5
print(f"Number of 5-qubit blocks: {num_blocks}")

print("\n--- Checking first 60 stabilizers ---")

# Check if the first set are local to blocks
# 0-14: XZZXIIIII... (XZZX at start of block)
# 15-29: IXZZXII... (XZZX at shift 1 of block)
# 30-44: XIXZZII... (XIXZZ at start of block)
# 45-59: ZXIXZII... (ZXIXZ at start of block)

patterns = [
    "XZZX_", # Pad with I? XZZX is 4 chars. Block is 5.
    "_XZZX", # IXZZX
    "XIXZZ",
    "ZXIXZ"
]

# Let's verify exactly what is in each block for the first 4 sets of 15 stabilizers.
for group_idx, pattern_name in enumerate(["XZZX", "IXZZX", "XIXZZ", "ZXIXZ"]):
    print(f"Checking group {group_idx} ({pattern_name})...")
    start_stab_idx = group_idx * 15
    end_stab_idx = (group_idx + 1) * 15
    for i in range(start_stab_idx, end_stab_idx):
        s = stabs[i]
        block_idx = i - start_stab_idx
        block_start = block_idx * 5
        block_content = s[block_start:block_start+5]
        
        # Check if rest is I
        rest_before = s[:block_start]
        rest_after = s[block_start+5:]
        if set(rest_before) - {'I'} or set(rest_after) - {'I'}:
             print(f"FAIL: Stabilizer {i} has non-I outside block {block_idx}")
        
        # Check content
        # For XZZX (length 4), it seems it is XZZX_ (padded with I)
        expected = ""
        if group_idx == 0: expected = "XZZXI"
        elif group_idx == 1: expected = "IXZZX"
        elif group_idx == 2: expected = "XIXZZ"
        elif group_idx == 3: expected = "ZXIXZ"
        
        if block_content != expected:
            print(f"FAIL: Stabilizer {i} block {block_idx} content {block_content} != {expected}")

print("\n--- Checking remaining stabilizers ---")
remaining = stabs[60:]
for i, s in enumerate(remaining):
    print(f"Rem {i}: {s}")
    # Check block structure
    # Are they composed of logical operators on blocks?
    # e.g. XXXXX on a block?
    block_ops = []
    for b in range(15):
        sub = s[b*5:(b+1)*5]
        if sub == "IIIII":
            block_ops.append("I")
        elif sub == "XXXXX":
            block_ops.append("X")
        elif sub == "ZZZZZ":
            block_ops.append("Z")
        else:
            block_ops.append(sub)
    print(f"  Blocks: {''.join(block_ops)}")
