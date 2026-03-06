import stim

def check_indices():
    target_x = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIII"
    target_z = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIII"
    
    stabs = []
    with open("stabilizers_84_task.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]
        for i, line in enumerate(lines):
            stabs.append(stim.PauliString(line))
            if line == target_x:
                print(f"Found target X at index {i}")
            if line == target_z:
                print(f"Found target Z at index {i}")

    # Check commutativity
    stab_x = stim.PauliString(target_x)
    stab_z = stim.PauliString(target_z)
    
    print("\nChecking commutativity for X target:")
    for i, s in enumerate(stabs):
        if not stab_x.commutes(s):
            print(f"Anticommutes with index {i}: {s}")

    print("\nChecking commutativity for Z target:")
    for i, s in enumerate(stabs):
        if not stab_z.commutes(s):
            print(f"Anticommutes with index {i}: {s}")

if __name__ == "__main__":
    check_indices()
