import json
import sys
import stim

# Load circuit
try:
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_35.stim", "r") as f:
        circuit_str = f.read()
except FileNotFoundError:
    print("Error: Circuit file not found.")
    sys.exit(1)

# Load corrected stabilizers
try:
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_35_corrected.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print("Error: Corrected stabilizers file not found.")
    sys.exit(1)

# Prepare tool input
tool_input = {
    "circuit": circuit_str,
    "stabilizers": stabilizers
}

# Save to a file for manual inspection if needed, or just to verify format
with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\check_35_input.json", "w") as f:
    json.dump(tool_input, f, indent=2)

print("Tool input prepared.")
