filename = r'C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\candidate_3.out'
with open(filename, 'r') as f:
    lines = f.readlines()

circuit_lines = []
flags = []
for line in lines:
    if line.startswith('FLAGS:'):
        # Parse flags
        # FLAGS:[49, 50, ...]
        content = line.strip().split(':')[1]
        flags = eval(content)
    else:
        circuit_lines.append(line.strip())

circuit_str = "\n".join(circuit_lines)
print("CIRCUIT_START")
print(circuit_str)
print("CIRCUIT_END")
print(f"FLAGS={flags}")
