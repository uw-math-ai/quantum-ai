import stim
import random

def get_metrics(circuit):
    cx_count = 0
    for op in circuit.flattened():
        if op.name == 'CX':
            cx_count += len(op.targets_copy()) // 2
    volume = len(list(circuit.flattened()))
    return cx_count, volume

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    stabilizers = [line.strip().replace('_', 'I') for line in lines if line.strip()]
    return stabilizers

def solve():
    stabilizers = load_stabilizers('current_task_stabilizers.txt')
    
    # We need a baseline to compare against
    # But we can just use the number 781
    best_cx = 781
    best_vol = 10000 # irrelevant if cx is worse
    
    print(f"Target to beat: CX={best_cx}")
    
    for i in range(10000):
        # Shuffle stabilizers
        current_stabs = list(stabilizers)
        random.shuffle(current_stabs)
        
        # Construct tableau
        try:
            # We need to construct a Tableau from stabilizers.
            # `stim.Tableau.from_stabilizers` maps Z_k to S_k.
            # But we want a state stabilized by S_k.
            # If we use `from_stabilizers`, the resulting tableau T satisfies T(Z_k) = S_k.
            # So T maps |0> to |psi>.
            # So we can synthesize T.
            
            # However, `from_stabilizers` requires full set of N stabilizers for N qubits.
            # We have 84 stabilizers but 85 qubits (indices up to 84).
            # Wait, let's check num qubits.
            # The prompt has 84 stabilizers.
            # The baseline uses indices up to 84. (So 85 qubits).
            # If we have 84 stabilizers for 85 qubits, the state is not fully stabilized?
            # Or one qubit is not involved?
            # Or one stabilizer is implicit?
            # `Tableau.from_stabilizers` requires N independent stabilizers.
            # If we pass 84, it might complain or pad.
            # Actually, `stim.Tableau.from_stabilizers` takes a list of Paulis.
            # If length < N, it raises error unless allow_underconstrained=True.
            
            paulis = [stim.PauliString(s) for s in current_stabs]
            tableau = stim.Tableau.from_stabilizers(paulis, allow_underconstrained=True)
            circuit = tableau.to_circuit(method="elimination")
            
            cx, vol = get_metrics(circuit)
            
            if cx < best_cx or (cx == best_cx and vol < best_vol):
                print(f"Found better: CX={cx}, Vol={vol} (iter {i})")
                best_cx = cx
                best_vol = vol
                with open('candidate_optimized.stim', 'w') as f:
                    f.write(str(circuit))
                    
        except Exception as e:
            # e.g. inconsistent stabilizers
            if i == 0:
                print(f"Error: {e}")
            pass

    print(f"Best found: CX={best_cx}, Vol={best_vol}")

if __name__ == "__main__":
    solve()
