import stim

def debug_stabilizer():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_133.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    target_idx = 54
    target_stab = stabilizers[target_idx]
    
    print(f"Target Stabilizer [{target_idx}]: {target_stab}")
    
    s_target = stim.PauliString(target_stab)
    
    conflicts = []
    for i, s_str in enumerate(stabilizers):
        if i == target_idx:
            continue
        s = stim.PauliString(s_str)
        if not s.commutes(s_target):
            print(f"Anticommutes with [{i}]: {s_str}")
            conflicts.append(i)
            
    if not conflicts:
        print("Commutes with all other stabilizers.")

if __name__ == "__main__":
    debug_stabilizer()
