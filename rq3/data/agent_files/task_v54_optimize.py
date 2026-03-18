import stim
import random
import time
import sys

def count_metrics(circuit):
    cx = 0
    vol = 0
    for instr in circuit:
        if instr.name in ['CX', 'CNOT']:
            cx += len(instr.targets_copy()) // 2
        
        if instr.name in ['CX', 'CNOT', 'CZ', 'H', 'S', 'SQRT_X', 'X', 'Y', 'Z', 'I']:
             vol += len(instr.targets_copy()) // (2 if instr.name in ['CX', 'CNOT', 'CZ'] else 1)
    return cx, vol

def main():
    try:
        with open('task_v54_stabilizers.txt', 'r') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        
        stabilizers = [stim.PauliString(l) for l in lines]
        num_qubits = len(stabilizers[0])
        print(f"Optimizing for {num_qubits} qubits.")

        # Baseline metrics (hardcoded from previous run analysis)
        best_cx = 270
        best_vol = 295
        print(f"Target to beat: CX<{best_cx} OR (CX={best_cx} AND Vol<{best_vol})")
        
        start_time = time.time()
        attempts = 0
        
        best_circuit = None
        
        while time.time() - start_time < 60:
            attempts += 1
            
            # Permutation: map q -> p
            perm = list(range(num_qubits))
            random.shuffle(perm)
            
            # Inverse: map p -> q
            inv_perm = [0] * num_qubits
            for q, p in enumerate(perm):
                inv_perm[p] = q
            
            # Create permuted stabilizers
            # Stab S acts on q with P. New stab S' acts on p=perm[q] with P.
            perm_stabilizers = []
            for s in stabilizers:
                s_str = str(s)
                phase = s_str[0]
                paulis = s_str[1:]
                
                new_paulis = ['I'] * num_qubits
                for q in range(num_qubits):
                    if q < len(paulis):
                         new_paulis[perm[q]] = paulis[q]
                
                perm_stabilizers.append(stim.PauliString(phase + "".join(new_paulis)))
            
            try:
                tableau = stim.Tableau.from_stabilizers(perm_stabilizers, allow_underconstrained=True)
                circ_perm = tableau.to_circuit(method="elimination")
                
                # Check metrics of permuted circuit
                # Note: permutation doesn't change gate counts, just indices.
                this_cx, this_vol = count_metrics(circ_perm)
                
                if this_cx <= best_cx:
                    is_better = False
                    if this_cx < best_cx:
                        is_better = True
                    elif this_cx == best_cx and this_vol < best_vol:
                        is_better = True
                    
                    if is_better:
                        print(f"Found IMPROVEMENT: CX={this_cx}, Vol={this_vol} (Attempt {attempts})")
                        best_cx = this_cx
                        best_vol = this_vol
                        
                        # Remap back: p -> inv_perm[p]
                        mapped_circuit = stim.Circuit()
                        for instr in circ_perm:
                            targets = instr.targets_copy()
                            new_targets = []
                            for t in targets:
                                if t.is_qubit_target:
                                    # Just use the integer for qubit target
                                    new_targets.append(inv_perm[t.value])
                                else:
                                    new_targets.append(t)
                            mapped_circuit.append(instr.name, new_targets, instr.gate_args_copy())
                        
                        best_circuit = mapped_circuit
                        with open('candidate_v54_opt.stim', 'w') as f:
                            f.write(str(best_circuit))
            except Exception as e:
                print(f"EXCEPTION: {e}")
                import traceback
                traceback.print_exc()
                pass

        print(f"Finished. Best found: CX={best_cx}, Vol={best_vol}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
