import stim

try:
    c = stim.Circuit.from_file(r"data/gemini-3-pro-preview/agent_files_ft/input.stim")
except:
    c = stim.Circuit.from_file(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\input.stim")

print(f"Num gates: {len(c)}")
print(f"Num qubits: {c.num_qubits}")

# Count slots for faults
# Approximate: len(c) * num_qubits * 3
# If 1000 gates * 105 qubits * 3 ~ 300,000 simulations.
# Stim is fast, but 300k might take a minute or two.
