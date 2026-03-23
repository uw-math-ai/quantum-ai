import re

def solve():
    circuit_str = """CX 30 0 0 30 30 0
H 0 3 13 16 21
CX 0 3 0 13 0 16 0 21 0 25 0 33
H 10 32
CX 10 0 32 0 25 1 1 25 25 1 1 20 1 33
H 5
CX 5 1 10 1 32 1 10 2 2 10 10 2 2 5 2 15 2 33
H 30
CX 30 2 20 3 3 20 20 3 3 33 5 3 15 3 32 3 30 4 4 30 30 4 4 5 5 15 5 33 15 6 6 15 15 6 6 33 33 7 7 33 33 7
H 7 15 24 29 34
CX 7 13 7 15 7 20 7 24 7 26 7 29 7 34
H 11 31
CX 11 7 31 7 15 8 8 15 15 8
H 21
CX 8 21 8 26 11 8 31 8 11 9 9 11 11 9
H 16
CX 9 16 9 21 9 26
H 25
CX 25 9 21 10 10 21 21 10 16 10 31 10 25 11 11 25 25 11 11 26 26 12 12 26 26 12 12 16 16 13 13 16 16 13 32 14 14 32 32 14
S 31 34
H 30 32 33
CX 14 24 14 27 14 29 14 30 14 31 14 32 14 33 14 34
H 26
CX 26 14 26 15 15 26 26 15
H 21
CX 15 21 15 22 33 15 21 16 16 21 21 16 16 17 16 27 33 17 17 33 33 17 17 27 33 18 18 33 33 18 22 18 27 19 19 27 27 19 19 22 22 20 20 22 22 20
H 26 31
CX 21 22 21 26 21 28 21 31 26 22 22 26 26 22 22 23 22 28 22 31 26 23 23 26 26 23 23 28 23 33 31 24 24 31 31 24
S 24
H 24
S 24
CX 24 26
H 30 32
CX 30 24 32 24 34 24 33 25 25 33 33 25 26 25 30 25 32 25 34 25 28 26 26 28 28 26 26 28 28 27 27 28 28 27 30 27 32 27 34 27 32 28 28 32 32 28
H 28 29 30 33
CX 28 29 28 30 28 33 33 29 29 33 33 29
H 31 34
CX 29 31 29 33 29 34 30 32 30 33 30 34
S 34
H 34
CX 33 31 34 31 33 32 34 32
S 34
H 24 25 27
S 24 24 25 25 27 27
H 24 25 27
S 0 0 2 2 4 4 7 7 9 9 11 11 22 22 23 23 27 27"""

    lines = circuit_str.split('\n')
    new_lines = []
    
    # Ancillas
    a14_1 = 35
    a14_2 = 37
    a21_1 = 36
    a21_2 = 38

    for line in lines:
        if line.strip().startswith("CX 14 24 14 27 14 29 14 30 14 31 14 32 14 33 14 34"):
            # Split logic for 14
            # 14 -> 35, 37 (Copies)
            # 14 -> 24 (Safe)
            # 35 -> 27 (Sensitive 1)
            # 14 -> 29 (Safe)
            # 14 -> 30 (Safe)
            # 37 -> 31 (Sensitive 2)
            # 14 -> 32 (Safe)
            # 14 -> 33 (Safe)
            # 37 -> 34 (Sensitive 3)
            # Uncompute 37, 35
            
            block = []
            block.append(f"CX 14 {a14_1}") # Copy 1
            block.append(f"CX 14 {a14_2}") # Copy 2
            
            # Original sequence logic: 24, 27, 29, 30, 31, 32, 33, 34
            block.append(f"CX 14 24")
            block.append(f"CX {a14_1} 27")
            block.append(f"CX 14 29")
            block.append(f"CX 14 30")
            block.append(f"CX {a14_2} 31")
            block.append(f"CX 14 32")
            block.append(f"CX 14 33")
            block.append(f"CX {a14_2} 34")
            
            block.append(f"CX 14 {a14_2}") # Uncompute 2
            block.append(f"CX 14 {a14_1}") # Uncompute 1
            
            new_lines.extend(block)
            
        elif line.strip().startswith("CX 21 22 21 26 21 28 21 31"):
            # Split logic for 21
            # 21 -> 36, 38
            # 36 -> 22, 26
            # 38 -> 28, 31
            
            parts = line.strip().split(" ")
            block = []
            
            block.append(f"CX 21 {a21_1}") # Copy 1
            block.append(f"CX 21 {a21_2}") # Copy 2
            
            block.append(f"CX {a21_1} 22")
            block.append(f"CX {a21_1} 26")
            block.append(f"CX {a21_2} 28")
            block.append(f"CX {a21_2} 31")
            
            block.append(f"CX 21 {a21_2}") # Uncompute 2
            block.append(f"CX 21 {a21_1}") # Uncompute 1
            
            new_lines.extend(block)
            
            if len(parts) > 9:
                rest = " ".join(parts[9:])
                # Need CX prefix
                new_lines.append(f"CX {rest}")
            
        else:
            new_lines.append(line)
            
    # Add measurements for ancillas
    new_lines.append(f"M {a14_1} {a21_1} {a14_2} {a21_2}")
    
    final_circuit = "\n".join(new_lines)
    
    with open("candidate_final.stim", "w") as f:
        f.write(final_circuit)
    
    print("Generated candidate_final.stim")

if __name__ == "__main__":
    solve()
