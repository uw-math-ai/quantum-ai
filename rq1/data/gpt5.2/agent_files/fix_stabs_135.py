import os

def fix():
    with open("stabilizers_135.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    new_lines = []
    for i, line in enumerate(lines):
        if len(line) != 135:
            print(f"Fixing line {i}, len {len(line)}")
            # For line 57, it seems to have extra characters.
            # Let's assume the first 135 are correct or we need to check.
            # But based on pattern, it should be I...IZZIZZI...I
            # Let's try to reconstruct it based on the pattern if possible, or just truncate if it looks like duplication.
            # Line 57 (index 57, so 58th line) starts with 47 'I's.
            if i == 57:
                 fixed = "I"*47 + "ZZIZZ" + "I"*83
                 print(f"Replaced line {i}")
                 new_lines.append(fixed)
            else:
                 new_lines.append(line)
        else:
            new_lines.append(line)

    with open("stabilizers_135.txt", "w") as f:
        f.write("\n".join(new_lines))

if __name__ == "__main__":
    fix()
