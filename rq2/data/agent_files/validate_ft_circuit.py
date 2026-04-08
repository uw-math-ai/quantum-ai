import stim
import sys

def get_circuit_text():
    return """
CX 2 0 0 2 2 0
H 0 4
CX 0 3 0 4
H 2
CX 2 0 3 1 1 3 3 1
H 1 2 4
CX 1 2 1 4
H 3
CX 3 1
H 3
CX 2 3
H 4
CX 4 2 4 3 3 4 4 3
H 3
CX 3 4
H 4
CX 4 3
H 2
S 2 2
H 2
S 0 0 2 2
"""

def build_ft_circuit():
    base = get_circuit_text()
    c = stim.Circuit(base)
    
    # Add checks
    # Stabilizers: XZZXI, IXZZX, XIXZZ, ZXIXZ, -IZXZI
    # Ancillas: 5, 6, 7, 8, 9
    # Indices in pauli string map to q0..q4
    
    checks = [
        ("XZZXI", 5, False), # False = 0 = +1
        ("IXZZX", 6, False),
        ("XIXZZ", 7, False),
        ("ZXIXZ", 8, False),
        ("IZXZI", 9, True)   # True = 1 = -1
    ]
    
    for pauli, anc, expected in checks:
        c.append("H", [anc])
        for q_idx, p in enumerate(pauli):
            if p == 'X':
                c.append("CX", [anc, q_idx])
            elif p == 'Z':
                c.append("CZ", [anc, q_idx])
            elif p == 'Y':
                c.append("CY", [anc, q_idx])
        c.append("H", [anc])
        c.append("M", [anc])
        
    return c, checks

def validate():
    ft_circuit, checks = build_ft_circuit()
    
    # Identify original operations for fault injection
    base_circuit = stim.Circuit(get_circuit_text())
    base_len = len(base_circuit) # Operations count?
    # Actually, we can just inject faults in the first part of ft_circuit.
    # But ft_circuit has more operations.
    # We need to map "fault in C" to "fault in ft_circuit".
    # The first N operations of ft_circuit correspond to C.
    
    # Count ops in base
    base_ops = 0
    for instr in base_circuit:
        if instr.name in ["CX", "H", "S", "X", "Y", "Z", "I", "SWAP", "CZ"]:
            # Decompose
            targets = instr.targets_copy()
            arity = 2 if instr.name in ["CX", "SWAP", "CZ"] else 1
            if arity == 2:
                base_ops += len(targets)//2
            else:
                base_ops += len(targets)
                
    print(f"Base operations (decomposed): {base_ops}")
    
    # We will simulate faults by using the "suffix" method on the FT circuit.
    # We only inject faults up to location base_ops + 1.
    
    # Decompose FT circuit
    ft_ops = []
    for instr in ft_circuit:
         if instr.name in ["CX", "H", "S", "X", "Y", "Z", "I", "SWAP", "CZ", "CY", "M"]:
            targets = instr.targets_copy()
            arity = 2 if instr.name in ["CX", "SWAP", "CZ", "CY"] else 1
            if instr.name == "M":
                # M is special, targets are 1
                for t in targets:
                    ft_ops.append((instr.name, [t.value]))
            elif arity == 2:
                for k in range(0, len(targets), 2):
                    ft_ops.append((instr.name, [t.value for t in targets[k:k+2]]))
            else:
                for t in targets:
                    ft_ops.append((instr.name, [t.value]))
                    
    # Pre-compute suffix tableaus for detection logic?
    # For FT, we need to check:
    # 1. Does fault trigger flag? (Measurement result != expected)
    # 2. If not, does fault cause error on Data > 1?
    
    # We can use TableauSimulator for this.
    # Simulating every fault is fast enough (38 ops * 5 * 3 = 600 sims).
    
    print("Simulating faults...")
    failures = []
    
    # Locations 0 to base_ops (inclusive, after last base op)
    # We iterate i from 0 to base_ops.
    # Note: ft_ops[0..base_ops-1] are the base ops.
    # ft_ops[base_ops] is the first check op.
    
    for i in range(base_ops + 1):
        for q in range(5): # Only faults on data qubits?
            # "spots(C) ... C[l <- P]"
            # C has 5 qubits.
            for p_char in ["X", "Y", "Z"]:
                # Construct circuit: Pre-fault + Fault + Post-fault
                
                sim = stim.TableauSimulator()
                
                # Pre-fault (ops 0 to i)
                for k in range(i):
                    op, targs = ft_ops[k]
                    sim.do(stim.Circuit(f"{op} " + " ".join(map(str, targs))))
                    
                # Fault
                if p_char == "X": sim.x(q)
                elif p_char == "Z": sim.z(q)
                elif p_char == "Y": sim.y(q)
                
                # Post-fault (remaining ops)
                for k in range(i, len(ft_ops)):
                    op, targs = ft_ops[k]
                    sim.do(stim.Circuit(f"{op} " + " ".join(map(str, targs))))
                
                # Check results
                # 1. Flags
                flags_triggered = False
                # Measurement results are in the simulator's measurement record.
                # But TableauSimulator doesn't store measurement record by default?
                # It does! sim.current_measurement_record()
                meas = sim.current_measurement_record()
                
                # Expected: [False, False, False, False, True]
                expected = [c[2] for c in checks]
                
                if len(meas) != 5:
                    print(f"Error: Expected 5 measurements, got {len(meas)}")
                    return
                
                for m_idx, m_val in enumerate(meas):
                    if m_val != expected[m_idx]:
                        flags_triggered = True
                        break
                
                # 2. Data Error
                # Compare final state on data qubits to ideal state.
                # Ideal state:
                # We can't easily compare states directly.
                # But we can check if it violates stabilizers of ideal code?
                # The ideal output is a specific state.
                # Error E = T_fault * T_ideal_inv ?
                # We want to know the weight of the error on data qubits 0..4.
                # The ancillas are measured and discarded.
                
                # Let's get the error Pauli string E on 0..4.
                # E = Propagated Fault.
                # We can compute E by propagating P forward through the FULL circuit (including checks).
                # But checks measure and reset.
                # However, for error weight analysis, we treat M as I?
                # No, M projects.
                # But "Error propagation" usually refers to Pauli propagation.
                # If we use the "difference" method:
                # Run ideal sim. Run faulty sim.
                # Compare frames?
                # Stim FrameSimulator is perfect for this.
                pass
                
                # Let's use FrameSimulator (sim.do with tracking?)
                # Actually, simpler:
                # We already know E_data from `analyze_circuit` (propagated through base).
                # The checks act on E_data.
                # Does E_data change passing through checks?
                # Checks are CNOTs. They propagate error to ancilla (flag) or back-propagate to data.
                # If checks are done carefully, they don't spread error on data (except phase).
                # But we just want to know: Did the flag fire?
                # If YES -> OK.
                # If NO -> Check Error Weight.
                
                if flags_triggered:
                    continue # Fault Tolerated.
                    
                # If flag NOT triggered, we must check the error weight.
                # The error on the data is the same as if we propagated P through base?
                # PLUS any back-action from checks?
                # If flag didn't trigger, it means the error commuted with the check?
                # Or the check failed to catch it.
                # If it commuted, the check didn't change it (except maybe phase).
                # So we can assume the error on data is the same as computed in `analyze_circuit`.
                # We computed E there.
                # Let's verify E's weight.
                
                # We can grab E from our previous analysis?
                # Or re-compute E here.
                # Re-compute E using simple propagation through BASE only.
                # (Since we assume if flag didn't fire, checks didn't mess it up significantly? 
                # Actually, checks might increase weight! 
                # But checks are transversal-ish (CNOT to separate ancillas).
                # A CNOT target->control (Z) spreads?
                # Check is CNOT ancilla -> data.
                # Ancilla is control. Data is target.
                # Z on Data -> Z on Ancilla. (Caught!)
                # X on Data -> X on Data. (Not caught by Z check, but caught by X check).
                # So checks don't spread X error on data.
                # Checks don't spread Z error on data (it goes to ancilla).
                # So the weight on data should be stable or decrease (if collapsed).
                # So using E from base circuit is conservative/correct.
                
                # So: Re-calculate E (propagated through base).
                # (We can cache this or just do it).
                
                # Propagate P through base suffix
                # We need the suffix tableau for location i.
                # Since i iterates 0..base_ops.
                # We can just build it on the fly.
                
                c_suffix = stim.Circuit()
                c_suffix.append("I", [0,1,2,3,4])
                for k in range(i, base_ops): # ops of base
                    op, targs = ft_ops[k]
                    c_suffix.append(op, targs)
                t_suffix = stim.Tableau.from_circuit(c_suffix).inverse()
                
                p_stim = stim.PauliString(5)
                if p_char == "X": p_stim[q] = 1
                elif p_char == "Z": p_stim[q] = 2
                elif p_char == "Y": p_stim[q] = 3
                
                e_final = t_suffix(p_stim)
                w = sum(1 for k in range(5) if e_final[k] != 0)
                
                if w > 1:
                    failures.append(f"Fault at {i} q{q} {p_char} (w={w}) NOT FLAGGED")

    if failures:
        print(f"FAILED: Found {len(failures)} unflagged high-weight faults.")
        for f in failures[:5]:
            print(f"  {f}")
    else:
        print("SUCCESS: All high-weight faults are flagged!")
        
    # Also verify stabilizers
    print("Verifying stabilizers...")
    sim = stim.TableauSimulator()
    sim.do(ft_circuit)
    # Check if data qubits 0..4 are stabilized by the 4 required stabilizers
    # (The state should be the same as ideal).
    # We can measure expectations.
    req_stabs = ["XZZXI", "IXZZX", "XIXZZ", "ZXIXZ"]
    for s_str in req_stabs:
        s = stim.PauliString(s_str)
        exp = sim.peek_observable_expectation(s)
        if exp != 1:
             print(f"STABILIZER FAIL: {s_str} -> {exp}")
             return

    print("Stabilizers preserved.")
    
    # Print the circuit for copy-paste
    print("\nFINAL CIRCUIT:")
    print(ft_circuit)

if __name__ == "__main__":
    validate()
