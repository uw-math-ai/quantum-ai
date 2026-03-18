with open("target_stabilizers_rq3.txt", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    s = line.strip()
    if not s: continue
    # Filter out line numbers if present (e.g. "1. XXX")
    if s[0].isdigit() and ". " in s:
        s = s.split(". ", 1)[1]
    
    # Truncate to 63 chars
    if len(s) > 63:
        s = s[:63]
    
    # Only keep lines that look like stabilizers (contain I, X, Z, Y)
    if not all(c in "IXZY" for c in s):
        continue
        
    new_lines.append(s)

with open("target_stabilizers_rq3.txt", "w") as f:
    f.write("\n".join(new_lines))

print(f"Fixed {len(new_lines)} stabilizers.")
