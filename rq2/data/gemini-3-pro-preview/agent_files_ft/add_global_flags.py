import re

def parse_circuit(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    gates = []
    for line in lines:
        parts = line.strip().split()
        if not parts: continue
        name = parts[0]
        targets = [int(x) for x in parts[1:]]
        gates.append((name, targets))
    return gates

gates = parse_circuit(r'C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\baseline.stim')

# Map data qubit -> flag qubit
# Data 0-48. Flags 49-97.
flag_map = {i: 49 + i for i in range(49)}
flag_qubits = list(flag_map.values())

new_lines = []

for name, targets in gates:
    if name == 'CX':
        # CX c1 t1 c2 t2 ...
        for i in range(0, len(targets), 2):
            c = targets[i]
            t = targets[i+1]
            fc = flag_map[c]
            ft = flag_map[t]
            
            # Sandwich
            new_lines.append(f"CX {c} {fc}")
            new_lines.append(f"CX {t} {ft}")
            new_lines.append(f"CX {c} {t}")
            new_lines.append(f"CX {t} {ft}")
            new_lines.append(f"CX {c} {fc}")
            
    elif name == 'H':
        # H t1 t2 ...
        # H changes X<->Z.
        # X error after H is dangerous.
        # So we check X after H.
        for t in targets:
            new_lines.append(f"H {t}")
            # Check X on t
            ft = flag_map[t]
            new_lines.append(f"CX {t} {ft}")
            new_lines.append(f"CX {t} {ft}") 
            # Wait, checking immediately after without operation in between?
            # CX t ft, CX t ft is Identity.
            # But if H created an error X?
            # H -> X (on t).
            # CX t ft -> ft flips.
            # CX t ft -> ft flips back.
            # Flags nothing.
            # So checking immediately doesn't work for generation.
            # We need the check to bracket the operation.
            # Before H: Check Z? (detects Z before it becomes X).
            # Z on control propagates? No.
            # So we don't need to check before.
            # We need to check AFTER H if the error spreads.
            # But the error spreads at the NEXT CX.
            # And the NEXT CX will be sandwiched.
            # So the next CX's sandwich will detect "incoming error".
            # So we don't need to wrap H explicitly!
            # The CX sandwich handles incoming propagation.
            pass
    else:
        # Other gates?
        pass

# Add init/meas?
# Input format implies implied init/meas or external.
# "All ancilla qubits must be initialized in the |0> state and measured at the end of the circuit."
# Stim handles implied init to |0>.
# We should list them in output?
# No, return_result expects just circuit string.

circuit_str = "\n".join(new_lines)
print(circuit_str)
print(f"FLAGS:{flag_qubits}")
