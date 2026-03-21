import sys

# Stabilizers from prompt
STABILIZERS = [
    "IIIIIXIIIXIXXIIII", "IIIIIIIIXIXIIXIXI", "IIIXIIIXIIIIIIXIX", "IIXIIIXIIIIIIIXIX",
    "IIIIXXXXXIXXIIIIX", "IXIIXIIIIIXIIXIII", "IIIIIIIIXXIXIIIXI", "XIXXIIIIIIIIIIXII",
    "IIIIIZIIIZIZZIIII", "IIIIIIIIZIZIIZIZI", "IIIZIIIZIIIIIIZIZ", "IIZIIIZIIIIIIIZIZ",
    "IIIIZZZZZIZZIIIIZ", "IZIIZIIIIIZIIZIII", "IIIIIIIIZZIZIIIZI", "ZIZZIIIIIIIIIIZII"
]

# Baseline circuit
BASELINE = """
CX 15 0 0 15 15 0
H 7
CX 7 0 11 0 16 0 5 1 1 5 5 1
H 1 2 3 4 6 15
CX 1 2 1 3 1 4 1 6 1 7 1 13 1 15 1 16 7 2 2 7 7 2 2 7 2 11 2 16 3 2 7 3 3 7 7 3 3 10 3 16 4 6 4 7 4 11 4 12 4 13 4 15 15 5 5 15 15 5
H 15
CX 5 6 5 8 5 12 5 15 7 6 6 7 7 6 6 12 6 16 10 7 7 10 10 7 7 12 11 7 15 8 8 15 15 8 8 9 8 12 8 14 10 8 10 9 9 10 10 9 9 10 9 12 9 15 10 12 10 13 11 10 12 10 13 10 14 10 16 10 14 11 11 14 14 11 11 12 11 15 13 11 15 12 12 15 15 12 13 12 15 13 13 15 15 13 14 13 16 13 16 14
"""

def generate_circuit():
    lines = [l.strip() for l in BASELINE.split('\n') if l.strip()]
    
    ancilla_start = 17
    ancilla = ancilla_start
    ancillas = []
    
    for stab in STABILIZERS:
        is_x = 'X' in stab
        is_z = 'Z' in stab
        
        targets = []
        for i, char in enumerate(stab):
            if char != 'I':
                targets.append(i)
        
        ancillas.append(ancilla)
        
        if is_x:
            # Measure X stabilizer -> Detects Z errors
            # Circuit: H a, CX a t..., H a
            lines.append(f"H {ancilla}")
            for t in targets:
                lines.append(f"CX {ancilla} {t}")
            lines.append(f"H {ancilla}")
            lines.append(f"M {ancilla}")
        elif is_z:
            # Measure Z stabilizer -> Detects X errors
            # Circuit: CX t a...
            for t in targets:
                lines.append(f"CX {t} {ancilla}")
            lines.append(f"M {ancilla}")
        
        ancilla += 1
        
    return "\n".join(lines), ancillas

if __name__ == "__main__":
    circuit_str, ancillas = generate_circuit()
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\candidate_final.stim", "w") as f:
        f.write(circuit_str)
    print("DONE")
