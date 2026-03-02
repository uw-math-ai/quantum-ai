import json

with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_135.stim", "r") as f:
    circuit_text = f.read()

with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_135.txt", "r") as f:
    stabilizers = [line.strip() for line in f if line.strip()]

print(json.dumps({"circuit": circuit_text, "stabilizers": stabilizers}))
