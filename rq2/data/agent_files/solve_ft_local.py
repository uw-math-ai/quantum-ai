import stim
import sys

def check_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    preserved = 0
    broken = []
    for i, s in enumerate(stabilizers):
        if sim.peek_observable_expectation(s) == 1:
            preserved += 1
        else:
            broken.append(i)
    return preserved, broken

def check_ft(circuit, data_qubits, flag_qubits, distance):
    threshold = (distance - 1) // 2
    # threshold = 4 for d=10.
    # If error weight >= 4, must be flagged.
    
    # We need to simulate single faults.
    # A fault is a Pauli X, Y, Z inserted after a gate.
    # For 2-qubit gates, it can be IX, XI, XX, etc. But single faults usually mean single location.
    # The prompt says: "A fault is a location in the circuit where there is an unexpected disruption (X, Y, Z Pauli gate)".
    # This implies single-qubit faults.
    # On a 2-qubit gate, a fault could be on control or target.
    
    # For efficiency, we can use stim's frame simulator or tableau simulator.
    # Since we need to check propagation, tableau is good but slow for many faults.
    # But the circuit is not too big (150 qubits, maybe 1000 gates).
    # Let's iterate over all gates and possible faults.
    
    gates = list(circuit)
    bad_faults = []
    
    for i, gate in enumerate(gates):
        if gate.name not in ["CX", "H", "R", "M"]:
            continue
        
        targets = gate.targets_copy()
        # For each target involved in the gate
        for t in targets:
            if not t.is_qubit_target:
                continue
            q = t.value
            
            for p in ["X", "Z"]: # Y is X*Z, usually covered by checking X and Z propagation.
                # Actually, Y can be distinct. But usually X and Z basis checks are enough.
                # Let's check X and Z.
                
                # We need to propagate this fault to the end.
                # We can use a tableau simulator, run the rest of the circuit.
                
                # Optimized way:
                # Run the whole circuit with a Pauli error injected at this point.
                # Measure the data qubits (in Z basis usually? No, the stabilizers check specific basis).
                # Wait, "propagates to ... data qubits".
                # This usually means we treat the circuit as a Clifford map and see how the error commutes through.
                # Yes, use Tableau.
                
                # Create a tableau for the REST of the circuit.
                rest_circuit = stim.Circuit()
                for g in gates[i+1:]:
                    rest_circuit.append(g)
                
                # Propagate the error Pauli
                P = stim.PauliString(circuit.num_qubits)
                P[q] = p
                
                # We need the tableau of the rest of the circuit.
                # Computing tableau for every fault is slow (O(G*Q)).
                # Total complexity O(G^2 * Q).
                # With G=1000, Q=150, G^2*Q = 10^6 * 150 = 1.5e8 operations. A bit slow for python.
                # But maybe G is smaller.
                
                # Better: Compute the tableau of the whole circuit ONCE.
                # Then for a fault at gate i, we need the tableau of gates[i+1:].
                # We can compute tableaus backwards?
                # Tableau(i) = Gate(i) * Tableau(i+1)
                # So we can start from end and update tableau.
                pass

    # Efficient implementation:
    # 1. Compute Tableau T_end = I
    # 2. Iterate backwards from last gate to first.
    # 3. At each step, update T_curr = Gate_i.inverse() * T_curr (actually Gate_i * T_curr if we move backwards?)
    #    Wait. If we have error E after gate i.
    #    The error at the end is T_{i+1...N}(E).
    #    Let T be the tableau of the rest of the circuit.
    #    Initially T is Identity.
    #    For gate G at step i (going backwards):
    #       - Check faults after G: apply T to error.
    #       - Update T: T = T.prepend(G) ? 
    #       stim.Tableau.prepend is not available.
    #       But we know T_new(P) = T_old( G(P) ).
    #       So if we maintain T as the map from "current time" to "end time".
    #       When we move from i+1 to i (backwards), we encounter gate G.
    #       The map from i to end is: apply G, then apply map from i+1 to end.
    #       So T_i(P) = T_{i+1}( G(P) ).
    #       So we just update the tableau by doing `T.do(G)`.
    #       Wait. `do` applies the gate.
    #       If we have a state, `do(G)` updates it.
    #       If we have a tableau representing a map. 
    #       Stim's Tableau `do` updates the tableau by appending the gate.
    #       If T represents the operation sequence S. `T.do(G)` represents S then G.
    #       We want the map FROM current point TO end.
    #       Let the circuit be G1, G2, ... GN.
    #       At step i, we want map M_i = G_{i+1} * ... * GN.
    #       M_{i-1} = G_i * M_i.
    #       So we start with Identity.
    #       Loop backwards.
    #       For each gate G:
    #          Prepend G to the sequence.
    #          Stim doesn't support prepending efficiently.
    #          BUT, Clifford conjugation is easy.
    #          We can just track the Pauli string!
    #          "Heisenberg picture".
    #          Start with single qubit Paulis at the end? No.
    #          We inject a fault at step i. We want to know what it becomes at the end.
    #          So we need to propagate specific Paulis forward.
    #          Forward simulation is O(G^2).
    #          
    #          Let's stick to the forward check for now.
    #          Maybe just sample some gates or check all?
    #          Let's check ALL. If it takes > 30s, we optimize.
    pass

    return bad_faults

def analyze_circuit():
    with open("input_circuit.stim", "r") as f:
        circuit_str = f.read()
    with open("stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
        
    circuit = stim.Circuit(circuit_str)
    
    # Check stabilizers
    stabilizers_parsed = [stim.PauliString(s) for s in stabilizers]
    preserved, broken = check_stabilizers(circuit, stabilizers_parsed)
    print(f"Preserved: {preserved}/{len(stabilizers)}")
    if broken:
        print(f"Broken indices: {broken[:10]}...")
        
    # Check FT
    data_qubits = list(range(150))
    flag_qubits = [] # Initially empty
    
    # We will just print the first few bad faults
    print("Checking faults (first 10)...")
    
    gates = list(circuit)
    count = 0
    
    # To be reasonably fast, let's just use stim.TableauSimulator for each check?
    # Or actually, we can iterate through the circuit and maintain the tableau?
    # No, that doesn't help with faults.
    
    # Let's try the backwards Heisenberg approach.
    # We want to know for each location i, and Pauli P, what is P_final = U_{i+1...N} P U_{i+1...N}^\dagger.
    # We can maintain the "inverse tableau" or just backpropagate Paulis?
    # Backpropagating a Pauli through a Clifford circuit is efficient.
    # But we have different Paulis for each location.
    #
    # Wait, we can iterate BACKWARDS through the circuit.
    # We maintain a SET of "active faults" that we are tracking? No.
    #
    # Actually, we can just run the forward simulation for each fault.
    # There are ~1000 gates. 1000 simulations is fine.
    # 1000 * 0.01s = 10s.
    
    bad_faults = []
    
    for i in range(len(gates)):
        gate = gates[i]
        if gate.name not in ["CX", "H"]:
            continue
            
        targets = gate.targets_copy()
        for t in targets:
            if not t.is_qubit_target: continue
            q = t.value
            
            for p_char in ["X", "Z"]:
                # Construct circuit from i+1 to end
                rest = stim.Circuit()
                for g in gates[i+1:]:
                    rest.append(g)
                
                # Propagate
                sim = stim.TableauSimulator()
                # Initialize state? No we propagate operators.
                # Use Tableau.
                tab = stim.Tableau(circuit.num_qubits)
                tab.do(rest)
                
                p = stim.PauliString(circuit.num_qubits)
                p[q] = p_char
                
                res = tab(p)
                
                # Check weight
                dw = sum(1 for k in data_qubits if res[k] != 0) # 0=I, 1=X, 2=Y, 3=Z
                fw = sum(1 for k in flag_qubits if res[k] != 0)
                
                # Check flag condition
                # Flagged if ANY flag qubit has X error (1) or Y error (2)? 
                # "triggers a flag ancilla (X error on a flag qubit)"
                # This usually means the flag qubit flips.
                # If we measure in Z basis, an X error flips the result.
                # So we check if X or Y component is present on flag?
                # Usually standard flags measure Z. So X or Y error is detected.
                
                flagged = False
                for k in flag_qubits:
                    if res[k] in [1, 2]: # X or Y
                        flagged = True
                        break
                
                if dw >= 4 and not flagged:
                    bad_faults.append({
                        "gate_idx": i,
                        "qubit": q,
                        "type": p_char,
                        "dw": dw,
                        "fw": fw
                    })
                    if len(bad_faults) >= 5:
                        break
            if len(bad_faults) >= 5: break
        if len(bad_faults) >= 5: break

    if bad_faults:
        print("Found bad faults:")
        for f in bad_faults:
            print(f)
    else:
        print("No bad faults found (in this scan)")

if __name__ == "__main__":
    analyze_circuit()
