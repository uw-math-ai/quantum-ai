import sys
sys.path.append(r'C:\Users\anpaz\Repos\quantum-ai\rq1')

# This is tricky because solve_133_v3.py has side effects (prints).
# I'll just read the file and eval the list part.
with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\solve_133_v3.py', 'r') as f:
    content = f.read()

# Extract the list
start = content.find("stabilizers = [")
end = content.find("]\n", start) + 1
stabs_str = content[start:end]
exec(stabs_str)

s5 = stabilizers[5]
s131 = stabilizers[131]

print(f"Checking s5 vs s131")
print(f"s5: {s5}")
print(f"s131: {s131}")

comm = 0
for i in range(len(s5)):
    c1 = s5[i]
    c2 = s131[i]
    if c1 != 'I' and c2 != 'I':
        if c1 != c2:
            comm += 1
            print(f"{i}: {c1} vs {c2} (anticommutes)")
        else:
            print(f"{i}: {c1} vs {c2} (commutes)")

# Print surrounding chars
print(f"s5[97:106]: {s5[97:106]}")
print(f"s131[97:106]: {s131[97:106]}")

print(f"Total anticommutations: {comm}")
print(f"Result: {'Commutes' if comm % 2 == 0 else 'Anticommutes'}")
