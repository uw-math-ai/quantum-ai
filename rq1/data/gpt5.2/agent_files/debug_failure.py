import stim

target = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXIIXIIIIIIIIIIIIIIIIIIIIII"
# This is the one from the tool output that failed.
# It corresponds to Line 42 in the file.

# Let's see if this line was trimmed in solve_105_gemini_task.py
with open("data/gemini-3-pro-preview/agent_files/stabilizers.txt", "r") as f:
    lines = [line.strip() for line in f if line.strip()]

line42 = lines[41]
print(f"File Line 42 len: {len(line42)}")
print(f"File Line 42: {line42}")

if len(line42) > 105:
    trimmed = line42[:105]
    print(f"Trimmed Line 42: {trimmed}")
    if trimmed == target:
        print("Trimmed version matches target")
    else:
        print("Trimmed version does NOT match target")
else:
    if line42 == target:
        print("Line 42 matches target")
    else:
        print("Line 42 does NOT match target")
