import ast
import stim
import sys

# Load bad faults
bad_faults = []
try:
    with open(r'C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\bad_faults.txt', 'r') as f:
        for line in f:
            bad_faults.append(ast.literal_eval(line))
except FileNotFoundError:
    print("bad_faults.txt not found")
    sys.exit(1)

print(f"Loaded {len(bad_faults)} bad faults.")

# Load stabilizers
stabilizers = []
try:
    with open('stabilizers.txt', 'r') as f:
        for line in f:
            s = line.strip()
            if s:
                stabilizers.append(s)
except FileNotFoundError:
    print("stabilizers.txt not found")
    sys.exit(1)

print(f"Loaded {len(stabilizers)} stabilizers.")

# Convert to stim.PauliString for efficiency
stab_objs = [stim.PauliString(s) for s in stabilizers]

covered_faults = set()
fault_to_stabs = {} # index -> list of stab indices
stab_to_faults = {} # stab_index -> set of fault indices

for i, fault in enumerate(bad_faults):
    p_str = fault['final_pauli']
    if p_str.startswith('+'): p_str = p_str[1:]
    
    # Pad or truncate to match stabilizers length
    if len(p_str) != len(stabilizers[0]):
        p_str = p_str[:len(stabilizers[0])] # Truncate to data qubits
    
    try:
        error_pauli = stim.PauliString(p_str)
    except Exception as e:
        print(f"Error parsing Pauli string {p_str}: {e}")
        continue
    
    detecting = []
    for j, stab in enumerate(stab_objs):
        if not error_pauli.commutes(stab):
            detecting.append(j)
            if j not in stab_to_faults: stab_to_faults[j] = set()
            stab_to_faults[j].add(i)
            
    fault_to_stabs[i] = detecting

# Greedy set cover
chosen_stabs = []
uncovered = set(range(len(bad_faults)))

print("Finding cover...")
while uncovered:
    best_stab = -1
    best_cover_count = -1
    best_covered_set = set()
    
    for j in stab_to_faults:
        # Intersect with currently uncovered
        covered_now = stab_to_faults[j].intersection(uncovered)
        count = len(covered_now)
        if count > best_cover_count:
            best_cover_count = count
            best_stab = j
            best_covered_set = covered_now
            
    if best_cover_count <= 0:
        print("Cannot cover all faults!")
        break
        
    chosen_stabs.append(best_stab)
    uncovered -= best_covered_set

print(f"Total stabilizers needed: {len(chosen_stabs)}")
print(f"Indices: {chosen_stabs}")

# Save chosen stabilizers
with open(r'C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\chosen_stabilizers.txt', 'w') as f:
    for idx in chosen_stabs:
        f.write(stabilizers[idx] + "\n")
