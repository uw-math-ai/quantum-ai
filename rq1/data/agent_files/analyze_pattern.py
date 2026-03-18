import stim

def analyze_indices():
    with open('stabilizers_90.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    for i in range(45, 75):
        if i >= len(lines): break
        line = lines[i]
        s = stim.PauliString(line)
        indices = [k for k in range(len(s)) if s[k] != 0]
        print(f"Line {i+1} (len {len(s)}): {indices}")

if __name__ == "__main__":
    analyze_indices()
