import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
stabs_path = os.path.join(script_dir, "stabilizers_196.txt")

with open(stabs_path, "r") as f:
    stabs = [line.strip() for line in f if line.strip()]

print(json.dumps(stabs))
