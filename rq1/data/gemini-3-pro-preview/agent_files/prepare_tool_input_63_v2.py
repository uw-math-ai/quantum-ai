import json

with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_63_attempt.stim", "r") as f:
    circuit_str = f.read()

with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_63.txt", "r") as f:
    stabs = [line.strip() for line in f if line.strip()]

output = {
    "circuit": circuit_str,
    "stabilizers": stabs
}

print(json.dumps(output))
