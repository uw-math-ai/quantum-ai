import stim
import sys

# Load stabilizers
try:
    with open("target_stabilizers.txt") as f:
        stabilizers_str = [line.strip() for line in f if line.strip()]
    stabilizers = [stim.PauliString(s) for s in stabilizers_str]
    print(f"Loaded {len(stabilizers)} stabilizers.")
except Exception as e:
    print(f"Error loading stabilizers: {e}")
    sys.exit(1)

# Method 1: Try synthesis directly from stabilizers
print("Attempting synthesis from stabilizers...")
try:
    # Check for consistency/independence not strictly required if we use allow_redundant=True
    # But if they are inconsistent (stabilize 0), it will fail or produce empty/bad tableau.
    t_new = stim.Tableau.from_stabilizers(
        stabilizers,
        allow_redundant=True,
        allow_underconstrained=True
    )
    print("Tableau successfully created from stabilizers.")
except Exception as e:
    print(f"Direct synthesis failed: {e}")
    print("Attempting to extract tableau from baseline circuit...")
    try:
        with open("baseline.stim") as f:
            baseline_circuit = stim.Circuit(f.read())
        
        # Verify baseline preserves stabilizers
        sim = stim.TableauSimulator()
        sim.do(baseline_circuit)
        valid = True
        for s in stabilizers:
            if sim.peek_observable_expectation(s) != 1:
                print(f"Baseline does NOT preserve stabilizer {s}")
                valid = False
                break
        
        if not valid:
            print("Baseline is invalid wrt target stabilizers! Cannot proceed with extraction.")
            sys.exit(1)
            
        # If valid, use the tableau from baseline
        # Note: baseline.to_tableau() gives the Heisenberg picture action U P U^dag.
        # But we want the state tableau (stabilizers of U|0>).
        # We can get this by running the circuit on a simulator and extracting the current inverse tableau?
        # Actually stim.TableauSimulator.current_inverse_tableau() gives the inverse.
        # Or just use circuit.to_tableau() BUT that is the channel tableau.
        # Wait, if we start with |0>, the stabilizers are Z0, Z1...
        # The output stabilizers are U Z_i U^dag.
        # So we can just take the tableau of the circuit, applied to Z_i?
        # No, stim.Circuit.to_tableau() returns the full tableau.
        # The stabilizers of the output state are the images of the input stabilizers (Z_i) under the circuit.
        # That is exactly what the Tableau object stores in its z_output.
        
        t_base = baseline_circuit.to_tableau()
        # However, we only care about the stabilizers that are in our target list.
        # The state is defined by the full set of stabilizers.
        # If the target stabilizers are a subset (underconstrained), we might pick any valid state.
        # But if we use the baseline's full state, it is definitely a valid one.
        t_new = t_base
        print("Tableau extracted from baseline.")

    except Exception as e2:
        print(f"Baseline extraction failed: {e2}")
        sys.exit(1)

# Synthesize using graph state
# method="graph_state" creates a circuit with H, S, CZ, sqrt(X). 
# It uses CZ (CX=0) which is optimal for cx_count.
print("Synthesizing graph state circuit...")
circuit_new = t_new.to_circuit(method="graph_state")

# Post-processing: Replace RX with H if valid
# Graph state synthesis might produce RX gates (reset/init).
# Since we assume input is |0>, RX is essentially init |+>.
# H on |0> also creates |+>.
# We need to be careful: if RX is used in the middle of the circuit on a qubit that is not |0>, it's different.
# But from_stabilizers and to_circuit(method='graph_state') usually produce a state preparation circuit 
# that acts on the input (assumed |0> usually) or resets qubits.
# If the circuit starts with RX, it's fine.
# Let's inspect the circuit.
# If we replace RX with H, we are assuming the qubit is in |0> right before the gate.
# In a fresh state prep circuit, yes.

circuit_final = stim.Circuit()
for instruction in circuit_new:
    if instruction.name == "RX":
        # Check if we can safely replace.
        # For a state prep circuit starting from |0>, RX target is equivalent to H target.
        # (RX resets to |0> then applies H -> |+>. If already |0>, H -> |+>).
        circuit_final.append("H", instruction.targets_copy())
    else:
        circuit_final.append(instruction)

# Save
with open("candidate_graph_v2.stim", "w") as f:
    f.write(str(circuit_final))

print("Candidate saved to candidate_graph_v2.stim")

# Quick metric check
cx = circuit_final.num_2_qubit_gates()
print(f"Candidate CX count: {cx}")

