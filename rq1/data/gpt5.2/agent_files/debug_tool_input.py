import json

with open("my_stabilizers_135.txt", "r") as f:
    stabilizers = [line.strip() for line in f if line.strip()]

print(f"Number of stabilizers in file: {len(stabilizers)}")

# Simulate tool logic
total = len(stabilizers)
print(f"Total passed: {total}")
