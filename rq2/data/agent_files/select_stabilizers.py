
import stim
import sys

input_circuit_str = """H 0 1 2 3 4 5 7 8 10 11 14 17 19 21 23
CX 0 1 0 2 0 3 0 4 0 5 0 7 0 8 0 10 0 11 0 14 0 17 0 19 0 21 0 23 0 42 0 48 42 1 1 42 42 1 1 27 44 2 2 44 44 2 2 27
H 6
CX 6 2 6 3 3 6 6 3
H 9 12 13 15 16 18 20 22
CX 3 9 3 12 3 13 3 15 3 16 3 18 3 20 3 22 3 27 3 33 33 4 4 33 33 4 4 46 12 4 36 4 46 5 5 46 46 5 5 39 12 5 36 5 39 6 6 39 39 6 18 6 36 6 24 7 7 24 24 7 19 7 39 8 8 39 39 8 8 10 8 11 8 14 8 17 8 19 8 21 8 23 8 24 8 27 8 33 8 39 8 42 8 44 8 46 8 48 27 9 9 27 27 9 9 30 27 10 10 27 27 10 10 12 10 13 10 15 10 16 10 18 10 20 10 22 10 30 36 11 11 36 36 11 12 11 15 12 18 13 13 18 18 13 15 13 19 14 14 19 19 14 42 14 42 15 15 42 42 15 15 21 15 23 15 28 15 33 15 36 15 39 15 44 15 46 24 16 16 24 24 16 16 17 16 19 16 27 16 28 16 30 16 48 30 17 17 30 30 17 17 34 18 20 18 22 18 24 18 34 18 42 42 19 19 42 42 19 19 20 19 40 20 40 21 23 21 25 21 44 21 46 33 22 22 33 33 22 22 25 22 28 22 36 22 39 28 23 23 28 28 23 23 31 27 24 24 27 27 24 24 30 24 31 24 34 24 42 24 48 34 25 25 34 34 25 25 37 27 26 26 27 27 26 26 33 26 37 26 40 40 27 27 40 40 27 44 28 28 44 44 28 28 34 28 44 28 46 34 29 29 34 34 29 29 34 39 30 30 39 39 30 30 31 30 34 30 36 31 35 42 32 32 42 42 32 32 35 32 37 32 39 32 48 37 33 33 37 37 33 33 41 37 34 34 37 37 34 34 41 44 35 35 44 44 35 35 40 46 36 36 46 46 36 36 37 36 40 37 42 46 38 38 46 46 38 38 42 38 44 44 39 39 44 44 39 39 46 44 40 40 44 44 40 40 41 40 46 40 48 44 42 42 44 44 42 43 42 44 42 45 42 46 42 47 42 48 42 44 43 45 43 46 43 47 43 48 43 45 44 46 44 47 44 48 44 46 45 47 45 48 45 47 46 48 46 48 47"""

stabilizers_str = """XXIIIIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIXXIIIIIXXIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIIIIXXIIIIIIIIIIII, IIIIIIIIXXIIIIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIXXIIIIIXXIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIIIIXXIIII, IIXXIIIIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIXXIIIIIXXIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIIIIXXIIIIIIIIII, IIIIIIIIIIXXIIIIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIXXIIIIIXXIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIIIIXXII, IIIIXXIIIIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIXXIIIIIXXIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIIIIXXIIIIIIII, IIIIIIIIIIIIXXIIIIIXXIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIXXIIIIIXXIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIIIIXX, IIIIIIXIIIIIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIXIIIIIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIXIIIIIIXIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIXIIIIIIXIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIIIIIIXIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIIIIIIXIIIIII, IIIIIIIZZIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIZZIIIIIZZIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIZZIIIII, IZZIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIZZIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIZZIIIIIIIIIII, IIIIIIIIIIIZZIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIZZIIIIIZZIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIZZIII, IIIZZIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIZZIIIIIZZIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIZZIIIIIIIII, IIIIIIIIIIIZZIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIZZIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIZZI, IIIIIZZIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIZZIIIIIZZIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIZZIIIIIII, ZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIII, IIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZII, IIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZ"""
stabilizers = [s.strip() for s in stabilizers_str.split(',')]

circuit = stim.Circuit(input_circuit_str)

# Map Qubit to its spread
# Simple BFS? No, just immediate children in the graph state logic?
# In a circuit, we can simulate the propagation.
# But "Faults" can happen anywhere.
# The critical ones are faults on "Control" (X) and "Target" (Z) of high degree nodes.
# Let's collect these "Bad Errors".

bad_errors = [] # List of sets of qubits

# Simulate X error on qubit q at the beginning
# For this, we can use Stim's tableau simulator to push Pauli strings
sim = stim.TableauSimulator()
sim.do(circuit)
# This gives the final state.
# But we want to know how an error propagates.
# We can use `stim.Circuit.explain_detector_error_model` if we had detectors.
# Or just push Pauli X/Z through the inverse circuit?
# No, push through the circuit.

# But simpler: Just trace the paths.
# Qubit 0 (Control of many CXs).
# X on 0 propagates to all targets of CXs where 0 is control.
# Let's find all `CX c t`.
cx_map = []
for instruction in circuit:
    if instruction.name == "CX":
        targets = instruction.targets_copy()
        for i in range(0, len(targets), 2):
            cx_map.append((targets[i].value, targets[i+1].value))

def propagate_X(qubit, cx_list):
    # If X on qubit, it spreads to targets of CXs where qubit is control
    # And keeps existing on qubit.
    # Note: X on control spreads to target.
    # But does it spread recursively?
    # In a sequence `CX 0 1, CX 1 2`.
    # X on 0 -> X on 1. Then X on 1 -> X on 2.
    # So yes, it spreads.
    # We need to respect the order of gates.
    error_state = {i: False for i in range(49)}
    error_state[qubit] = True
    
    for c, t in cx_list:
        if error_state[c]:
            error_state[t] = not error_state[t] # X spreads
    
    return [q for q, has_err in error_state.items() if has_err]

def propagate_Z(qubit, cx_list):
    # Z spreads from target to control
    # But we must traverse circuit in reverse?
    # No, if fault happens at start.
    # `CX 0 1`. Z on 1 (target) spreads to 0 (control).
    # Z on 0 stays.
    # So we traverse Forward.
    error_state = {i: False for i in range(49)}
    error_state[qubit] = True
    
    for c, t in cx_list:
        if error_state[t]:
            error_state[c] = not error_state[c] # Z spreads back
            
    return [q for q, has_err in error_state.items() if has_err]

# Identify bad faults (weight >= 3)
bad_faults = [] # List of (type, qubit, resulting_weight, resulting_error_set)

# Check X faults on all qubits at start (or after H layer)
for q in range(49):
    res = propagate_X(q, cx_map)
    if len(res) >= 3:
        bad_faults.append(('X', q, len(res), set(res)))

# Check Z faults
for q in range(49):
    res = propagate_Z(q, cx_map)
    if len(res) >= 3:
        bad_faults.append(('Z', q, len(res), set(res)))

print(f"Found {len(bad_faults)} bad faults.")
if len(bad_faults) > 0:
    print(f"Example: {bad_faults[0]}")

# Now find stabilizers to detect them.
# A stabilizer S detects error E if they anti-commute.
# Convert stabilizers to Pauli strings.
# And Errors to Pauli strings.
# Check commutation.

def pauli_commutes(stab_str, error_set, error_type):
    # stab_str: "XXII..."
    # error_set: {0, 1, 2}
    # error_type: 'X' or 'Z' (all qubits in error_set have this error)
    # Anti-commute if overlap is odd number of anti-commuting positions.
    # X and Z anti-commute.
    # X and X commute. Z and Z commute. I commutes.
    
    anticommutes = 0
    for q in error_set:
        if q >= len(stab_str): continue
        p = stab_str[q]
        if p == 'I': continue
        if error_type == 'X':
            if p == 'Z': anticommutes += 1
        elif error_type == 'Z':
            if p == 'X': anticommutes += 1
    
    return (anticommutes % 2) == 0 # Returns True if commutes (undetected)

undetected = []
for bf in bad_faults:
    etype, q, w, eset = bf
    detected = False
    for stab in stabilizers:
        if not pauli_commutes(stab, eset, etype):
            detected = True
            break
    if not detected:
        undetected.append(bf)

print(f"Undetected bad faults: {len(undetected)}")

# We need to measure a set of stabilizers.
# Let's greedily pick stabilizers to detect the bad faults.
# We want to minimize the number of stabilizers measured?
# Or maybe just include enough.

needed_stabilizers = []
remaining_faults = bad_faults[:]

while len(remaining_faults) > 0:
    # Score each stabilizer
    best_stab = None
    best_count = -1
    
    for stab in stabilizers:
        if stab in needed_stabilizers: continue
        
        count = 0
        for bf in remaining_faults:
            etype, q, w, eset = bf
            if not pauli_commutes(stab, eset, etype):
                count += 1
        
        if count > best_count:
            best_count = count
            best_stab = stab
            
    if best_count <= 0:
        print("Cannot detect remaining faults!")
        break
        
    needed_stabilizers.append(best_stab)
    print(f"Selected stabilizer detecting {best_count} faults. Total needed: {len(needed_stabilizers)}")
    
    # Remove detected
    new_remaining = []
    for bf in remaining_faults:
        etype, q, w, eset = bf
        if pauli_commutes(best_stab, eset, etype):
            new_remaining.append(bf)
    remaining_faults = new_remaining

print(f"Total stabilizers to measure: {len(needed_stabilizers)}")

# Analyze weights
weights = []
for s in needed_stabilizers:
    w = 0
    for char in s:
        if char != 'I': w += 1
    weights.append(w)
print(f"Weights: {weights}")

