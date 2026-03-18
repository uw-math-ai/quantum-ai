import stim

def fix_stabilizers():
    with open('stabilizers_90.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    # Construct correct Line 61 (index 60)
    # Z at 0, 15, 30, 60, 73, 74
    # Length 90
    s_list = ['I'] * 90
    for idx in [0, 15, 30, 60, 73, 74]:
        s_list[idx] = 'Z'
    correct_s60 = "".join(s_list)
    
    print(f"Replacing line 60 (len {len(lines[60])}) with corrected version (len {len(correct_s60)})")
    lines[60] = correct_s60
    
    with open('stabilizers_90.txt', 'w') as f:
        for line in lines:
            f.write(line + '\n')

if __name__ == "__main__":
    fix_stabilizers()
