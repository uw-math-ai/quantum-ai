import json
import sys
# add current dir to path to import solve_152
sys.path.append(r"C:\Users\anpaz\Repos\quantum-ai\rq1")
import solve_152

with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\stabilizers.json", "w") as f:
    json.dump(solve_152.stabilizers, f)
