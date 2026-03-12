import sys
from agent_tools import evaluate_optimization

with open("candidate_1.stim", "r") as f:
    circuit_text = f.read()

print("Submitting candidate...")
try:
    result = evaluate_optimization(candidate=circuit_text)
    print(result)
except Exception as e:
    print(f"Error: {e}")
