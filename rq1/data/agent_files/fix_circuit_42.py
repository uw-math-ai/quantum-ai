import stim
import re

with open("circuit_attempt_42.stim", "r") as f:
    content = f.read()

# Stim output from to_circuit might have wrapped lines if printed weirdly or if the python console wrapped it.
# But here I am reading the file directly.
# Let's inspect if the file has newlines in the middle of instructions.

print("--- START FILE CONTENT ---")
print(content)
print("--- END FILE CONTENT ---")

# If the file content has lines starting with numbers, it means the previous line was wrapped.
# We can fix this by joining lines that start with numbers to the previous line.

lines = content.split('\n')
fixed_lines = []
for line in lines:
    line = line.strip()
    if not line: continue
    
    # If line starts with a number, append to last line
    if line[0].isdigit():
        if fixed_lines:
            fixed_lines[-1] += " " + line
        else:
            # This shouldn't happen for a valid circuit unless it starts with a number?
            # CX 0 1 is valid.
            fixed_lines.append(line)
    else:
        fixed_lines.append(line)

fixed_content = '\n'.join(fixed_lines)

with open("circuit_attempt_42_fixed.stim", "w") as f:
    f.write(fixed_content)

print("Fixed circuit written to circuit_attempt_42_fixed.stim")
