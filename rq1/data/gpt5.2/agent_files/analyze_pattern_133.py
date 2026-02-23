import sys

with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\solve_133_v3.py', 'r') as f:
    content = f.read()

start = content.find("stabilizers = [")
end = content.find("]\n", start) + 1
stabs_str = content[start:end]
exec(stabs_str)

print("Pattern analysis:")
for i, s in enumerate(stabilizers):
    if "ZZZZZ" in s:
        # Find indices of Z
        indices = [j for j, c in enumerate(s) if c == 'Z']
        print(f"{i}: {indices} (len {len(s)})")
