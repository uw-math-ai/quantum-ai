
with open("data/agent_files/target_stabilizers.txt", "r") as f:
    content = f.read()

# Split by comma
stabs = content.split(',')
cleaned_stabs = [s.strip() for s in stabs if s.strip()]

with open("data/agent_files/target_stabilizers.txt", "w") as f:
    for s in cleaned_stabs:
        f.write(s + "\n")

print(f"Fixed {len(cleaned_stabs)} stabilizers.")
