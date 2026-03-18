import stim

def solve():
    with open("target_stabilizers_task_v10.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    # Remove index 58 (line 59)
    # Be careful with indices. The previous script said index 58 failed.
    # 0-indexed.
    if len(lines) > 58:
        removed = lines.pop(58)
        print(f"Removed stabilizer 58: {removed}")
    else:
        print("Error: not enough lines")
        return

    with open("target_stabilizers_fixed.txt", "w") as f:
        for line in lines:
            f.write(line + "\n")

    print(f"Wrote {len(lines)} stabilizers to target_stabilizers_fixed.txt")

if __name__ == "__main__":
    solve()
