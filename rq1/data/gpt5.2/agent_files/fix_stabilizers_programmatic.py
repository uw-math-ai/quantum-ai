import os

def fix():
    print("Reading stabilizers...")
    file_path = r"data\gemini-3-pro-preview\agent_files\stabilizers_152.txt"
    with open(file_path, "r") as f:
        stabilizers = [line.strip() for line in f.readlines() if line.strip()]

    print(f"Number of stabilizers: {len(stabilizers)}")
    
    fixed_stabilizers = []
    for i, s in enumerate(stabilizers):
        if len(s) == 152:
            fixed_stabilizers.append(s)
        else:
            print(f"Fixing stabilizer {i} (length {len(s)})")
            if len(s) > 152:
                # Remove trailing Is
                diff = len(s) - 152
                new_s = s[:-diff]
                print(f"Shortened to {len(new_s)}")
                fixed_stabilizers.append(new_s)
            elif len(s) < 152:
                # Add trailing Is
                diff = 152 - len(s)
                new_s = s + "I" * diff
                print(f"Lengthened to {len(new_s)}")
                fixed_stabilizers.append(new_s)
                
    with open(file_path, "w") as f:
        f.write('\n'.join(fixed_stabilizers))
        
    print("Stabilizers file updated.")

if __name__ == "__main__":
    fix()
