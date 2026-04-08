import stim
import sys
import numpy as np
import os

# Load data
try:
    import current_task_data
except ImportError:
    sys.path.append(os.getcwd())
    try:
        import current_task_data
    except ImportError:
        sys.exit("Could not import current_task_data")

STABILIZERS = current_task_data.stabilizers
DATA_QUBITS = current_task_data.data_qubits

def check_stabilizers(circuit_path, stabilizers):
    try:
        circuit = stim.Circuit.from_file(circuit_path)
    except Exception as e:
        return 0, len(stabilizers), list(range(len(stabilizers)))
        
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    preserved = 0
    total = len(stabilizers)
    failed = []
    
    for i, stab_str in enumerate(stabilizers):
        ps = stim.PauliString(stab_str)
        if sim.peek_observable_expectation(ps) == 1:
            preserved += 1
        else:
            failed.append(i)
            
    return preserved, total, failed

def check_fault_tolerance(circuit_path, data_qubits, distance):
    threshold = (distance - 1) // 2 # 4
    circuit = stim.Circuit.from_file(circuit_path)
    
    num_qubits = circuit.num_qubits
    flag_qubits = [q for q in range(num_qubits) if q not in data_qubits]
    
    fault_list = [] # List of (description, stim.PauliString)
    
    def to_int(x, z):
        if x and z: return 2
        if x: return 1
        if z: return 3
        return 0

    # 1. Collect all fault locations
    # We will just simulate propagation by running forward
    
    # Initialize active faults list (empty)
    active_faults = [] # (desc, ps)
    
    gate_idx = 0
    for instruction in circuit:
        name = instruction.name
        targets = instruction.targets_copy()
        
        # Update existing faults
        if name == "H":
            for t in targets:
                if t.is_qubit_target:
                    q = t.value
                    for i in range(len(active_faults)):
                        desc, ps = active_faults[i]
                        val = ps[q]
                        if val == 1: ps[q] = 3
                        elif val == 3: ps[q] = 1
        elif name == "CX":
            for k in range(0, len(targets), 2):
                c = targets[k].value
                t = targets[k+1].value
                for i in range(len(active_faults)):
                    desc, ps = active_faults[i]
                    # CX propagates X_c -> X_c X_t, Z_t -> Z_c Z_t
                    vc = ps[c]
                    vt = ps[t]
                    xc = (vc == 1 or vc == 2)
                    zc = (vc == 3 or vc == 2)
                    xt = (vt == 1 or vt == 2)
                    zt = (vt == 3 or vt == 2)
                    
                    new_xc = xc
                    new_zc = zc ^ zt # Z_c gets Z_t? No.
                    # Z_t -> Z_c Z_t.
                    # Z_c -> Z_c.
                    # Wait.
                    # Propagate P through CX.
                    # Z_c -> Z_c.
                    # Z_t -> Z_c Z_t.
                    # So Z_c_new = Z_c_old.
                    # Z_t_new = Z_t_old ^ Z_c_old?
                    # No.
                    # P_out = CX P_in CX.
                    # If P_in = Z_t, P_out = Z_c Z_t.
                    # So Z_t contributes to Z_c output? No.
                    # Z_t (on target) becomes Z_c Z_t.
                    # So Z_c_out has contribution from Z_t_in?
                    # Let's check.
                    # Z_c_out = Z_c_in + Z_t_in?
                    # No.
                    # Z_c_in -> Z_c_out.
                    # Z_t_in -> Z_c_out + Z_t_out.
                    # So Z_c_out = Z_c_in + Z_t_in.
                    # Z_t_out = Z_t_in.
                    # X_c_in -> X_c_out + X_t_out.
                    # X_t_in -> X_t_out.
                    # So X_t_out = X_t_in + X_c_in.
                    # X_c_out = X_c_in.
                    
                    # My previous logic:
                    # new_zc = zc ^ zt
                    # new_xt = xt ^ xc
                    # Was that correct?
                    # If I have Z_t (zt=1), then new_zc = 0^1 = 1. new_zt = 1.
                    # Result Z_c Z_t. Correct.
                    # If I have X_c (xc=1), then new_xt = 0^1 = 1. new_xc = 1.
                    # Result X_c X_t. Correct.
                    # Correct.
                    
                    new_xc = xc
                    new_zc = zc ^ zt
                    new_xt = xt ^ xc
                    new_zt = zt
                    
                    ps[c] = to_int(new_xc, new_zc)
                    ps[t] = to_int(new_xt, new_zt)

        # Inject new faults
        for t in targets:
            if t.is_qubit_target:
                q = t.value
                gate_idx += 1
                for p_type in [1, 2, 3]:
                    new_ps = stim.PauliString(num_qubits)
                    new_ps[q] = p_type
                    active_faults.append( (f"gate_{gate_idx}_{name}_q{q}_type{p_type}", new_ps) )
                    
    # Check weights
    bad_faults = []
    total_bad = 0
    undetected = 0
    
    for desc, ps in active_faults:
        w = 0
        for q in data_qubits:
            if q < len(ps) and ps[q] != 0:
                w += 1
        
        if w >= 4:
            total_bad += 1
            flagged = False
            for f in flag_qubits:
                if f < len(ps) and ps[f] in [1, 2]: # X or Y
                    flagged = True
                    break
            
            if not flagged:
                undetected += 1
                bad_faults.append( (desc, w) )
                
    score = 1.0
    if total_bad > 0:
        score = 1.0 - (undetected / total_bad)
        
    return score, bad_faults

if __name__ == "__main__":
    circuit_file = "candidate_initial.stim"
    if len(sys.argv) > 1:
        circuit_file = sys.argv[1]
        
    p, t, f = check_stabilizers(circuit_file, STABILIZERS)
    print(f"Stabilizers: {p}/{t}")
    
    score, bad_faults = check_fault_tolerance(circuit_file, DATA_QUBITS, 9)
    print(f"FT Score: {score}")
    print(f"Bad faults: {len(bad_faults)}")
    if bad_faults:
        for d, w in bad_faults[:5]:
            print(f"  {d}: {w}")
