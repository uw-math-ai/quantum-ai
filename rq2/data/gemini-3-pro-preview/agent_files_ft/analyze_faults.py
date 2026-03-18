import json
import sys

def parse_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def anticommutes(p1, p2):
    # p1 is dict {qubit_idx: 'X'/'Y'/'Z'}, p2 is string
    # or both strings?
    # validation output gives dict. stabilizer is string.
    # Convert stabilizer to dict or list
    anti_count = 0
    # Loop over indices in p1
    for q_idx_str, p_char in p1.items():
        q_idx = int(q_idx_str)
        if q_idx >= len(p2):
            continue
        stab_char = p2[q_idx]
        
        if p_char == 'I' or stab_char == 'I':
            continue
        if p_char == stab_char:
            continue
        # Different non-identity Paulis anticommute
        anti_count += 1
    
    return (anti_count % 2) == 1

def analyze(json_file, stab_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    stabilizers = parse_stabilizers(stab_file)
    
    errors = data.get('error_propagation', [])
    if not errors:
        print("No errors found.")
        return

    print(f"Analyzing {len(errors)} errors...")
    
    stab_scores = {s: 0 for s in stabilizers}
    undetected_count = 0
    
    for err in errors:
        final_paulis = err['final_paulis'] # Dict {idx: char}
        detected = False
        for s in stabilizers:
            if anticommutes(final_paulis, s):
                stab_scores[s] += 1
                detected = True
        
        if not detected:
            undetected_count += 1
            # print(f"Undetected error: {err}")

    print(f"Undetected errors: {undetected_count}")
    
    # Sort stabilizers by score
    sorted_stabs = sorted(stab_scores.items(), key=lambda x: x[1], reverse=True)
    
    print("\nTop stabilizers:")
    for s, score in sorted_stabs[:10]:
        print(f"{s}: {score}")

if __name__ == "__main__":
    analyze(sys.argv[1], sys.argv[2])
