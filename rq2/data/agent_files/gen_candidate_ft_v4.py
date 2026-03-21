
import stim
from inputs_task import circuit_str, stabilizers

def generate():
    next_ancilla = 49
    new_lines = []
    ancillas = []
    
    for s_idx, s in enumerate(stabilizers):
        terms = []
        for q, char in enumerate(s):
            if char in 'XYZ':
                terms.append((q, char))
        
        if not terms:
            continue
            
        anc = next_ancilla
        flag = next_ancilla + 1
        ancillas.append(anc)
        ancillas.append(flag)
        next_ancilla += 2
        
        new_lines.append(f"H {anc}")
        
        # Split: ensure second_half <= 2 (Extra safe)
        if len(terms) <= 2:
            first_half = []
            second_half = terms
        else:
            split_idx = len(terms) - 2
            first_half = terms[:split_idx]
            second_half = terms[split_idx:]
            
        for q, p in first_half:
            if p == 'X': new_lines.append(f"CX {anc} {q}")
            elif p == 'Z': new_lines.append(f"CZ {anc} {q}")
            elif p == 'Y': new_lines.append(f"CY {anc} {q}")
            
        new_lines.append(f"CX {anc} {flag}")
        
        for q, p in second_half:
            if p == 'X': new_lines.append(f"CX {anc} {q}")
            elif p == 'Z': new_lines.append(f"CZ {anc} {q}")
            elif p == 'Y': new_lines.append(f"CY {anc} {q}")
            
        new_lines.append(f"H {anc}")
        new_lines.append(f"M {anc} {flag}")
        
    final_circuit = circuit_str + "\n" + "\n".join(new_lines)
    
    with open("ancillas.txt", "w") as f:
        f.write(",".join(map(str, ancillas)))
    
    with open("candidate.stim", "w") as f:
        f.write(final_circuit)

if __name__ == "__main__":
    generate()
