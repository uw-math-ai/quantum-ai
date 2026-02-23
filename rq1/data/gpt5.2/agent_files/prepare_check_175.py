import json

def load_file(filename):
    with open(filename, 'r') as f:
        return f.read().strip()

def load_lines(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip()]

circuit = load_file("data/gemini-3-pro-preview/agent_files/circuit_175_generated.stim")
stabilizers = load_lines("data/gemini-3-pro-preview/agent_files/stabilizers_current.txt")

output = {
    "circuit": circuit,
    "stabilizers": stabilizers
}

print(json.dumps(output, indent=2))
