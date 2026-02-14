import json
import os

def generate_tool_input():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\target_stabilizers_63_v2.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]
    
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\circuit_attempt_63.stim", "r") as f:
        circuit = f.read()

    tool_input = {
        "circuit": circuit,
        "stabilizers": stabs
    }
    
    print(json.dumps(tool_input))

if __name__ == "__main__":
    generate_tool_input()
