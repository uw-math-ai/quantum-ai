import json

# Read circuit
with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_150_v2.stim", "r") as f:
    circuit_str = f.read()

# Read stabilizers
with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_150_v2.txt", "r") as f:
    stabilizers = [line.strip() for line in f if line.strip()]

# Create tool input dictionary
tool_input = {
    "circuit": circuit_str,
    "stabilizers": stabilizers
}

# Write to file
with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\tool_input.json", "w") as f:
    json.dump(tool_input, f)
