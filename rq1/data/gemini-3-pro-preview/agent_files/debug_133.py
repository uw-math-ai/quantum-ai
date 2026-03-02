import stim

def analyze_failure():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_133.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    failed_stab = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIIXXIIXXXIIIIIIIIIIIIIIIIIIIIIIIII"
    
    try:
        idx = stabilizers.index(failed_stab)
        print(f"Failed stabilizer index: {idx}")
    except ValueError:
        print("Failed stabilizer not found in list")
        return

    # Check commutativity with all other stabilizers
    s_failed = stim.PauliString(failed_stab)
    anticommuting = []
    for i, s_str in enumerate(stabilizers):
        if i == idx:
            continue
        s = stim.PauliString(s_str)
        if not s.commutes(s_failed):
            anticommuting.append((i, s_str))
            
    print(f"Stabilizer {idx} anticommutes with {len(anticommuting)} other stabilizers:")
    for i, s in anticommuting:
        print(f"  {i}: {s}")

if __name__ == "__main__":
    analyze_failure()
