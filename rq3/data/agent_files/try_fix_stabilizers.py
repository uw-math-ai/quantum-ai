
import stim

def load_stabs(filename):
    with open(filename, "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    return lines

def check_consistency(stabs):
    try:
        ps = [stim.PauliString(s) for s in stabs]
        # Check commutation
        for i in range(len(ps)):
            for j in range(i+1, len(ps)):
                if ps[i].commutes(ps[j]) == False:
                    # print(f"Anticommute: {i} and {j}")
                    return False
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def try_fix(stabs, mode="start"):
    fixed_stabs = []
    for i, s in enumerate(stabs):
        if len(s) == 196:
            fixed_stabs.append(s)
        else:
            diff = 196 - len(s)
            if diff > 0: # Too short
                if mode == "start":
                    fixed_stabs.append("I" * diff + s)
                else:
                    fixed_stabs.append(s + "I" * diff)
            else: # Too long
                diff = -diff
                if mode == "start":
                    fixed_stabs.append(s[diff:])
                else:
                    fixed_stabs.append(s[:-diff])
    return fixed_stabs

lines = load_stabs("data/agent_files/target_stabilizers.txt")

print("Checking original...")
if check_consistency(lines):
    print("Original is consistent!")
else:
    print("Original is inconsistent.")

print("Trying fix (start)...")
fixed_start = try_fix(lines, "start")
if check_consistency(fixed_start):
    print("Fix (start) IS CONSISTENT!")
    with open("data/agent_files/target_stabilizers_fixed.txt", "w") as f:
        for s in fixed_start:
            f.write(s + "\n")
    # Overwrite target
    with open("data/agent_files/target_stabilizers.txt", "w") as f:
        for s in fixed_start:
            f.write(s + "\n")
else:
    print("Fix (start) is inconsistent.")

print("Trying fix (end)...")
fixed_end = try_fix(lines, "end")
if check_consistency(fixed_end):
    print("Fix (end) IS CONSISTENT!")
else:
    print("Fix (end) is inconsistent.")
