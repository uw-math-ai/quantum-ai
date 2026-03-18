import stim
import json

# JSON data from validate_circuit output
analysis_data = {
    "fault_tolerance": False,
    "error_propagation": [
        {"loc": 29, "gate": "CX", "fault_qubit": 46, "fault_pauli": "Y", "final_paulis": {"3": "Y", "4": "X", "6": "X", "8": "Z", "9": "Z", "13": "Z", "14": "Z", "16": "Z", "17": "Z", "20": "Z", "21": "Z", "23": "Z", "24": "X", "25": "X", "27": "X", "28": "Z", "30": "Z", "31": "Z", "34": "Z", "38": "X", "39": "X", "41": "X", "42": "Z", "43": "Z", "45": "Z"}, "data_weight": 25, "flag_weight": 0},
        {"loc": 10, "gate": "CX", "fault_qubit": 46, "fault_pauli": "Y", "final_paulis": {"1": "Z", "3": "Y", "4": "X", "6": "X", "8": "Z", "9": "Z", "13": "Z", "14": "Z", "16": "Z", "17": "Z", "20": "Z", "24": "X", "25": "X", "27": "X", "28": "Z", "29": "Z", "31": "Z", "38": "X", "39": "X", "41": "X", "42": "Z", "43": "Z", "45": "Z"}, "data_weight": 23, "flag_weight": 0},
        {"loc": 138, "gate": "CX", "fault_qubit": 15, "fault_pauli": "Y", "final_paulis": {"15": "Y", "16": "Z", "20": "Z", "21": "X", "22": "X", "23": "X", "24": "X", "25": "X", "26": "X", "27": "X", "28": "X", "29": "X", "31": "X", "35": "X", "36": "X", "37": "X", "38": "X", "39": "X", "40": "X", "41": "X", "42": "X", "43": "X", "45": "X"}, "data_weight": 23, "flag_weight": 0},
        {"loc": 90, "gate": "CX", "fault_qubit": 8, "fault_pauli": "Y", "final_paulis": {"8": "Y", "9": "Z", "13": "Z", "21": "X", "22": "X", "23": "X", "24": "X", "25": "X", "26": "X", "27": "X", "28": "X", "29": "X", "31": "X", "35": "X", "36": "X", "39": "X", "41": "X", "42": "X", "43": "X", "46": "X", "48": "X"}, "data_weight": 21, "flag_weight": 0},
        {"loc": 138, "gate": "CX", "fault_qubit": 15, "fault_pauli": "X", "final_paulis": {"15": "X", "21": "X", "22": "X", "23": "X", "24": "X", "25": "X", "26": "X", "27": "X", "28": "X", "29": "X", "31": "X", "35": "X", "36": "X", "37": "X", "38": "X", "39": "X", "40": "X", "41": "X", "42": "X", "43": "X", "45": "X"}, "data_weight": 21, "flag_weight": 0},
        {"loc": 9, "gate": "CX", "fault_qubit": 45, "fault_pauli": "Y", "final_paulis": {"1": "Z", "3": "Z", "7": "Z", "9": "Z", "10": "Z", "13": "Z", "15": "Z", "16": "Z", "20": "Z", "24": "X", "25": "X", "27": "X", "28": "Z", "29": "Z", "31": "Z", "35": "Z", "36": "Z", "38": "Y", "39": "X", "41": "X"}, "data_weight": 20, "flag_weight": 0},
        {"loc": 29, "gate": "CX", "fault_qubit": 46, "fault_pauli": "X", "final_paulis": {"3": "X", "4": "X", "6": "X", "8": "Z", "9": "Z", "13": "Z", "15": "Z", "16": "Z", "20": "Z", "21": "Z", "23": "Z", "24": "X", "25": "X", "27": "X", "29": "Z", "30": "Z", "34": "Z", "38": "X", "39": "X", "41": "X"}, "data_weight": 20, "flag_weight": 0},
        {"loc": 29, "gate": "CX", "fault_qubit": 3, "fault_pauli": "Y", "final_paulis": {"3": "Z", "8": "Z", "9": "Z", "13": "Z", "14": "Z", "16": "Z", "17": "Z", "20": "Z", "21": "Z", "23": "Y", "25": "X", "26": "X", "27": "X", "28": "Z", "30": "Z", "31": "Z", "34": "Z", "42": "Z", "43": "Z", "45": "Z"}, "data_weight": 20, "flag_weight": 0},
        {"loc": 30, "gate": "CX", "fault_qubit": 46, "fault_pauli": "X", "final_paulis": {"3": "X", "4": "X", "6": "X", "8": "Z", "9": "Z", "13": "Z", "15": "Z", "16": "Z", "20": "Z", "21": "Z", "23": "Z", "24": "X", "25": "X", "27": "X", "29": "Z", "30": "Z", "34": "Z", "38": "X", "39": "X", "41": "X"}, "data_weight": 20, "flag_weight": 0},
        {"loc": 85, "gate": "H", "fault_qubit": 44, "fault_pauli": "Y", "final_paulis": {"8": "Z", "9": "Z", "13": "Z", "15": "Z", "16": "Z", "20": "Z", "21": "X", "22": "X", "24": "X", "28": "X", "29": "Y", "30": "Z", "31": "X", "34": "Z", "35": "X", "36": "X", "38": "X", "42": "X", "43": "X", "45": "X"}, "data_weight": 20, "flag_weight": 0}
    ],
    "preserved_stabilizers": 48
}

stabilizers_str = """
IIXIXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIXIXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIXIXXXIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIXIXXXIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXXXIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXXXIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXXX
IXIXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIXIXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIXIXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIXIXIXXIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXXIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXXIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXX
XXXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIXXXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIXXXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIXXXIIXIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXIIXIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXIIXIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXIIXI
IIZIZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIZIZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIZIZZZIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIZIZZZIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZZZIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZZZIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZZZ
IZIZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIZIZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIZIZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIZIZIZZIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZZIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZZIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZZ
ZZZIIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIZZZIIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIZZZIIZIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIZZZIIZIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZIIZIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZIIZIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZIIZI
XXIXIIIXXIXIIIIIIIIIIIIIIIIIXXIXIIIXXIXIIIIIIIIII
XXIXIIIIIIIIIIXXIXIIIIIIIIIIXXIXIIIIIIIIIIXXIXIII
IIIIIIIIIIIIIIIIIIIIIXXIXIIIXXIXIIIXXIXIIIXXIXIII
ZZIZIIIZZIZIIIIIIIIIIIIIIIIIZZIZIIIZZIZIIIIIIIIII
ZZIZIIIIIIIIIIZZIZIIIIIIIIIIZZIZIIIIIIIIIIZZIZIII
IIIIIIIIIIIIIIIIIIIIIZZIZIIIZZIZIIIZZIZIIIZZIZIII
"""
stabilizers = [line.strip() for line in stabilizers_str.split('\n') if line.strip()]

# Load circuit
with open("input.stim", "r") as f:
    circuit_str = f.read()
circuit = stim.Circuit(circuit_str)

# 1. Check preservation
sim = stim.TableauSimulator()
sim.do(circuit)
broken_stab_indices = []
for i, s in enumerate(stabilizers):
    p = stim.PauliString(s)
    if sim.peek_observable_expectation(p) != 1:
        broken_stab_indices.append(i)
        print(f"Stabilizer {i} is NOT preserved: {s}")

# 2. Select stabilizers to measure
faults = analysis_data["error_propagation"]
selected_stabs = []

def check_anticommute(stab_str, error_map):
    comm = 0
    for q_idx_str, p_char in error_map.items():
        q_idx = int(q_idx_str)
        if q_idx < len(stab_str):
            s_char = stab_str[q_idx]
            if s_char == 'I' or p_char == 'I': continue
            if s_char != p_char: comm += 1
    return (comm % 2) == 1

uncovered = list(range(len(faults)))
flag_idx = 49
new_lines = []
flag_qubits = []

while uncovered:
    best_s_idx = -1
    best_cover = []
    
    for s_idx, s in enumerate(stabilizers):
        # Prefer simpler stabilizers (fewer non-I)?
        # Or just greedy.
        cover = []
        for f_idx in uncovered:
            if check_anticommute(s, faults[f_idx]["final_paulis"]):
                cover.append(f_idx)
        
        if len(cover) > len(best_cover):
            best_cover = cover
            best_s_idx = s_idx
            
    if best_s_idx != -1:
        selected_stabs.append(stabilizers[best_s_idx])
        # Add measurement logic
        stab = stabilizers[best_s_idx]
        ancilla = flag_idx
        flag_idx += 1
        flag_qubits.append(ancilla)
        
        # Build gadget
        # H anc
        new_lines.append(f"H {ancilla}")
        for q, p in enumerate(stab):
            if p == 'X': new_lines.append(f"CX {ancilla} {q}")
            elif p == 'Z': new_lines.append(f"CZ {ancilla} {q}")
            elif p == 'Y': new_lines.append(f"CY {ancilla} {q}")
        new_lines.append(f"H {ancilla}")
        new_lines.append(f"M {ancilla}")
        
        uncovered = [u for u in uncovered if u not in best_cover]
    else:
        print("Could not cover remaining faults:", uncovered)
        break

print(f"Added {len(selected_stabs)} flag ancillas.")

# Construct final circuit
final_circuit_str = str(circuit) + "\n" + "\n".join(new_lines)

# Write output
with open("gen_ft_solution.stim", "w") as f:
    f.write(final_circuit_str)

print("FLAGS=" + str(flag_qubits))
