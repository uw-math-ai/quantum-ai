import stim
import sys
sys.path.append('.')
from find_bad_faults import analyze_faults

bad_faults = analyze_faults('input.stim', 3)

stabilizers = []
with open('stabilizers.txt', 'r') as f:
    for line in f:
        if line.strip():
            stabilizers.append(stim.PauliString(line.strip()))

stab_tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
inv_stab_tableau = stab_tableau.inverse()

def is_stabilizer(p):
    p_slice = p[:135]
    p_mapped = inv_stab_tableau(p_slice)
    s = str(p_mapped)
    return 'X' not in s and 'Y' not in s

for f in bad_faults:
    p_str = f['error_string']
    p = stim.PauliString(p_str)
    
    detected = False
    for s in stabilizers:
        if not p.commutes(s):
            detected = True
            break
    
    if not detected:
        print(f"Undetected fault: {f}")
