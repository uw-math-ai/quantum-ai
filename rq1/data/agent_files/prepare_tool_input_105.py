import json
with open('circuit_candidate_105.stim', 'r') as f:
    circuit = f.read()
with open('my_stabilizers_105.txt', 'r') as f:
    stabs = [l.strip() for l in f if l.strip()]

print(json.dumps({"circuit": circuit, "stabilizers": stabs}))
