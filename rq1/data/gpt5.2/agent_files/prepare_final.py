import json
import sys

# Since I cannot call final_circuit directly from python (it's a tool in the LLM environment),
# I will print the circuit content to a file in a clean way (one command per line) 
# so I can copy it safely.

with open(r"data\gemini-3-pro-preview\agent_files\circuit_42.stim", "r") as f:
    circuit = f.read()

# Stim circuits from tableau.to_circuit() are usually well formatted.
# I'll just print it to a file `circuit_final.txt` to be sure.
with open(r"circuit_final.txt", "w") as f:
    f.write(circuit)

print("Written to circuit_final.txt")
