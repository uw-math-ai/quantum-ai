
import stim
import sys

# Load circuit
circuit_str = """CX 14 0 0 14 14 0
H 0 7 14
CX 0 7 0 14 0 35 0 45 0 46
H 42 43
CX 42 0 43 0 7 1 1 7 7 1 1 28 1 35 1 45 1 46 42 1 43 1 14 2 2 14 14 2 2 21 2 35 46 3 3 46 46 3 3 28 3 45 30 3 32 3 34 3 37 3 39 3 41 3 42 3 43 3 48 3 21 4 4 21 21 4 28 4 30 4 32 4 34 4 37 4 39 4 41 4 48 4 35 5 5 35 35 5 5 28 28 6 6 28 28 6 30 6 32 6 34 6 37 6 39 6 41 6 48 6 15 7 7 15 15 7
H 7 8 15
CX 7 8 7 15 7 36 7 45 42 7 42 8 8 42 42 8
H 17 20 28 44 46
CX 8 17 8 20 8 28 8 29 8 44 8 46 8 48 42 8 15 9 9 15 15 9 9 22 9 29 9 42 9 45 29 10 10 29 29 10 10 45 36 10 42 10 22 11 11 22 22 11 36 11 36 12 12 36 36 12 12 45 42 12 42 13 13 42 42 13 16 14 14 16 16 14
H 14 15 16
CX 14 15 14 16 14 37 14 45 43 14 43 15 15 43 43 15
H 19 35
CX 15 17 15 19 15 30 15 35 15 44 15 46 43 15 16 23 16 30 16 43 16 45 30 17 17 30 30 17 17 45 37 17 43 17 23 18 18 23 23 18 37 18 37 19 19 37 37 19 19 45 43 19 43 20 20 43 43 20 30 21 21 30 30 21
H 29
CX 21 29 21 38 21 46 21 47 44 21 29 22 22 29 29 22 22 31 22 38 22 47 44 22 46 23 23 46 46 23 23 24 23 38 47 24 24 47 47 24 24 31 32 24 39 24 44 24 45 24 47 25 25 47 47 25 31 25 32 25 39 25 45 25 38 26 26 38 38 26 26 31 31 27 27 31 31 27 32 27 39 27 45 27 46 28 28 46 46 28
H 28 29 30
CX 28 29 28 30 28 39 44 28 44 29 29 44 44 29 29 32 29 35 29 37 29 43 29 46 29 48 44 29 30 32 30 44 30 47 32 31 31 32 32 31 39 31 44 31 47 32 32 47 47 32 39 32 39 33 33 39 39 33 44 33 44 34 34 44 44 34 37 35 35 37 37 35
H 36
CX 35 36 35 37 35 40 35 45 36 39 36 40 36 45 37 38 37 40 45 38 38 45 45 38 38 39 41 38 44 38 48 38 45 39 39 45 45 39 41 39 44 39 45 39 48 39 40 45 45 41 41 45 45 41 44 41 45 41 48 41 43 42 42 43 43 42
H 43
CX 42 43 42 45 42 46 43 44 43 45 43 48 46 44 44 46 46 44 44 45 44 47 44 48 46 45 45 46 46 45 46 45 48 45 47 46 46 47 47 46 47 46 48 46"""

stabs_str = "IIXIXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIXIXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIXIXXXIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIXIXXXIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXXXIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXXXIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXXX, IXIXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIXIXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIXIXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIXIXIXXIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXXIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXXIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXX, XXXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIXXXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIXXXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIXXXIIXIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXIIXIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXIIXIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXIIXI, IIZIZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIZIZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIZIZZZIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIZIZZZIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZZZIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZZZIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZZZ, IZIZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIZIZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIZIZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIZIZIZZIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZZIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZZIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZZ, ZZZIIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIZZZIIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIZZZIIZIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIZZZIIZIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZIIZIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZIIZIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZIIZI, XXIXIIIXXIXIIIIIIIIIIIIIIIIIXXIXIIIXXIXIIIIIIIIII, XXIXIIIIIIIIIIXXIXIIIIIIIIIIXXIXIIIIIIIIIIXXIXIII, IIIIIIIIIIIIIIIIIIIIIXXIXIIIXXIXIIIXXIXIIIXXIXIII, ZZIZIIIZZIZIIIIIIIIIIIIIIIIIZZIZIIIZZIZIIIIIIIIII, ZZIZIIIIIIIIIIZZIZIIIIIIIIIIZZIZIIIIIIIIIIZZIZIII, IIIIIIIIIIIIIIIIIIIIIZZIZIIIZZIZIIIZZIZIIIZZIZIII"

circuit = stim.Circuit(circuit_str)
stabilizers = [stim.PauliString(s.strip()) for s in stabs_str.split(',')]

# Filter weight 4 stabilizers
w4_stabilizers = [s for s in stabilizers if sum(1 for c in str(s) if c not in '_I') == 4]

# Simulate faults
# For each gate, inject Pauli X, Y, Z.
# Propagate to end.
# Check weight.
# Check if anti-commits with any w4 stabilizer.

# We need a simulator.
sim = stim.TableauSimulator()
# sim.do(circuit) # Removed full simulation
# Inverse tableau to propagate errors forward? 
# Or just use the tableau to find the effect of errors.
# The tableau maps input Paulis to output Paulis.
# But here we have faults in the middle.
# Efficient way: 
# Iterate gates. For each gate, apply it to the tableau.
# Inject error -> Apply P.
# Then apply rest of circuit.
# But that's slow (gates * 3 * gates).
# Faster: Backward propagation?
# Propagate Z and X from each qubit backwards?
# No, forward is better for "faults".
# Actually, Stim has `peek_observables` or similar? No.
# Just use `stim.Circuit.explain_detector_error_model`? No, that requires detectors.
# We don't have detectors yet.

# Let's brute force it. The circuit is short enough.
# Approx 200 gates?
# 200 * 3 = 600 faults.
# Each simulation takes milliseconds.
# 600 * 1ms = 0.6s. Very fast.

bad_faults = 0
unflagged_bad_faults = 0
total_faults = 0

print(f"Analyzing {len(circuit)} instructions...")

# Convert circuit to operations list for manual stepping
ops = list(circuit)

# Baseline: Error-free output state (stabilized by stabilizers)
# We don't need the state, just the error propagation.
# But wait, the error propagation depends on the gates.
# We can compute the "Pauli transfer" of the remaining circuit.
# For each location `k` (0 to N-1):
#   Rest of circuit `C_k` = ops[k+1:]
#   Fault `P` at location `k` (after op k).
#   Propagate `P` through `C_k`.
#   Resulting error `E`.
#   Check weight(E).

# To do this efficiently:
# Compute the tableau of the full circuit `T`.
# But we need the tableau of the suffix.
# Suffix tableaus can be computed by composing inverses?
# Or just re-running.

for k in range(len(ops)):
    # Run the prefix to get state? No need, Pauli propagation is state-independent for Clifford circuits.
    # We just need to propagate P through ops[k+1:].
    
    # But wait, does the gate at `k` itself cause the fault?
    # "at each gate location... injects single-qubit Pauli faults".
    # Usually this means *after* the gate.
    # If the gate is 2-qubit, we inject on both targets?
    # "For each location l in spots(C)... C[l <- P]"
    # Usually "spots" means every qubit line at every time step.
    # So if we have `CX 0 1`, we can have faults on 0 or 1 before/after?
    # The definition says: "spots(C) be the set of valid fault locations... C[l <- P] denote... inserting P at location l".
    # This usually implies inserting a gate P into the circuit.
    # Inserting P before or after a gate is equivalent (up to gate commutation).
    # We'll assume inserting *after* each operation on the qubits involved.
    
    op = ops[k]
    targets = op.targets_copy()
    # Filter only qubit targets (ignore sweep bits etc, but here only Clifford gates)
    qubits = [t.value for t in targets if t.is_qubit_target]

    # Construct the rest of the circuit
    rest = stim.Circuit()
    for j in range(k+1, len(ops)):
        rest.append(ops[j])

    # Ensure rest uses qubit 48 to force tableau size >= 49
    # Clone rest to avoid modifying it if shared (but here it's fresh)
    # Actually, modifying rest is fine as it's created fresh each iteration.
    rest.append(stim.CircuitInstruction("I", [stim.GateTarget(48)]))
    
    # Construct tableau
    if len(rest) == 0:
        tab = stim.Tableau(49) # Identity
    else:
        tab = stim.Tableau.from_circuit(rest)
    
    # Apply op to simulator to update state (we assume faults happen AFTER op)
    # Wait, we need to check faults AFTER the op.
    # So apply op first.
    sim.do(op)
    
    # Check targets
    targets_indices = [t.value for t in op.targets_copy() if t.is_qubit_target]
    
    for q in targets_indices:
        for p_name in ['X', 'Y', 'Z']:
            # Check if fault is harmless
            # Construct PauliString for the fault
            p_fault = stim.PauliString(49)
            if p_name == 'X': p_fault[q] = 1
            elif p_name == 'Y': p_fault[q] = 2
            elif p_name == 'Z': p_fault[q] = 3
            
            # Check expectation
            # Use peek_observable_expectation if available, else ...
            # Stim 1.12+ has it.
            try:
                exp = sim.peek_observable_expectation(p_fault)
                if abs(exp) > 0.999:
                    # Harmless
                    continue
            except AttributeError:
                # Fallback? Assumed available.
                pass

            if p_name == 'X':
                out_ps = tab.x_output(q)
            elif p_name == 'Y':
                out_ps = tab.y_output(q)
            elif p_name == 'Z':
                out_ps = tab.z_output(q)
            
            # Count weight
            w = 0
            # Ensure out_ps covers up to 48
            limit = min(len(out_ps), 49)
            for i in range(limit):
                if out_ps[i] != 0:
                    w += 1
            
            # If tableau is smaller than 49 (e.g. circuit uses few qubits), the rest are I.
            # But here circuit uses up to 48.
            
            total_faults += 1
            if w >= 4:
                bad_faults += 1
                # Check commutativity with weight 4 stabilizers
                caught_w4 = False
                for s in w4_stabilizers:
                    if not s.commutes(out_ps):
                        caught_w4 = True
                        break
                
                if not caught_w4:
                    unflagged_bad_faults += 1
                    # Check if caught by ANY stabilizer
                    caught_any = False
                    for s in stabilizers:
                        if not s.commutes(out_ps):
                            caught_any = True
                            break
                    
                    if not caught_any:
                        print(f"Fault at op {k} ({op}) qubit {q} Pauli {p_name}: Weight {w}, Uncaught by ANY")
                        print(f"Output Pauli: {out_ps}")
                        # Print first 5
                        if unflagged_bad_faults > 5:
                            sys.exit(0)
                    else:
                        pass # Caught by weight 12

print(f"Total faults: {total_faults}")
print(f"Bad faults (wt>=4): {bad_faults}")
print(f"Unflagged bad faults (by W4): {unflagged_bad_faults}")

