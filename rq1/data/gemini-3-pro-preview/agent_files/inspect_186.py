import stim

def inspect():
    with open(r'data/gemini-3-pro-preview/agent_files/stabilizers_186.txt') as f:
        lines = [line.strip() for line in f if line.strip()]

    stabilizers = [stim.PauliString(line) for line in lines]
    
    indices = [3, 9, 39, 51, 57, 105]
    print("Group 1 (105 conflicts with rest):")
    for idx in indices:
        print(f"{idx}: {lines[idx]}")
        
    indices = [7, 103, 145, 151, 163, 169]
    print("\nGroup 2 (7 conflicts with rest):")
    for idx in indices:
        print(f"{idx}: {lines[idx]}")

    indices = [97, 13, 55, 61, 73, 79]
    print("\nGroup 3 (97 conflicts with rest):")
    for idx in indices:
        print(f"{idx}: {lines[idx]}")

if __name__ == "__main__":
    inspect()
