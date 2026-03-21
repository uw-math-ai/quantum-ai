import sys

def anticommutes(p1, p2):
    # p1 is stabilizer op on q. p2 is fault on q.
    if p1 == 'I': return False # Stabilizer is Identity on q => Commutes
    if p2 == 'I': return False # Fault is Identity => Commutes
    if p1 == p2: return False # Same Pauli => Commutes
    return True # Different Paulis => Anticommute

def get_weight(stab):
    return sum(1 for c in stab if c != 'I')

with open(r'C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\stabilizers.txt', 'r') as f:
    content = f.read().strip()
    # Remove newlines and split by comma
    stabs = [s.strip() for s in content.replace('\n', '').split(',')]

bad_faults = [
    (1, 'Y'), 
    (72, 'Y'), 
    (74, 'Y'), 
    (26, 'Z'), 
    (26, 'Y'), 
    (27, 'Z'), 
    (27, 'Y')
]

for q, error_pauli in bad_faults:
    print(f"Fault: Qubit {q}, Pauli {error_pauli}")
    candidates = []
    for idx, s in enumerate(stabs):
        if q < len(s):
            stab_op = s[q]
            # Check anticommutation
            # Pauli Y anticommutes with X and Z
            # Pauli Z anticommutes with X and Y
            # Pauli X anticommutes with Y and Z
            
            is_anti = False
            if error_pauli == 'Y':
                if stab_op in ['X', 'Z']: is_anti = True
            elif error_pauli == 'Z':
                if stab_op in ['X', 'Y']: is_anti = True
            elif error_pauli == 'X':
                if stab_op in ['Y', 'Z']: is_anti = True
                
            if is_anti:
                candidates.append((idx, s, get_weight(s)))
    
    # Sort by weight
    candidates.sort(key=lambda x: x[2])
    
    if candidates:
        best = candidates[0]
        print(f"  Best stabilizer: Index {best[0]}, Weight {best[2]}")
        print(f"  String: {best[1]}")
    else:
        print("  No detecting stabilizer found!")
