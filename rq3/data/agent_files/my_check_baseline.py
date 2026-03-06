import stim
import sys

def solve():
    print("Reading my_stabilizers.txt...")
    with open("my_stabilizers.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]
    
    print(f"Number of stabilizers: {len(stabs)}")
    print(f"Length of stabilizer 0: {len(stabs[0])}")
    
    print("Reading my_baseline.stim...")
    with open("my_baseline.stim", "r") as f:
        baseline_text = f.read()
    
    baseline = stim.Circuit(baseline_text)
    print(f"Baseline qubits: {baseline.num_qubits}")
    
    # Check preservation
    tableau = stim.Tableau.from_circuit(baseline)
    
    preserved = 0
    total = len(stabs)
    
    # We must pad the tableau if baseline uses fewer qubits than stabilizers?
    # Tableau size matches baseline num_qubits.
    # If stabilizers act on more qubits, we need to extend the tableau.
    # But usually baseline defines the system size.
    # If stabilizers length > baseline.num_qubits, we have a mismatch.
    
    if len(stabs[0]) > baseline.num_qubits:
        print(f"Warning: Stabilizers length ({len(stabs[0])}) > Baseline qubits ({baseline.num_qubits}).")
        # Extend tableau?
        # A circuit on N qubits implicitly acts as Identity on qubit N+1, N+2...
        # So we can extend the tableau with identity.
        # But let's see.
        pass
        
    for s_str in stabs:
        # Pad stabilizer string to match tableau size? Or vice versa?
        # Stim PauliString length must match tableau length for operations.
        # If tableau is smaller, we can't apply it to larger PauliString.
        # We need a tableau of size len(s_str).
        
        # Create full tableau of size len(s_str)
        # Initialize with Identity.
        # Then apply circuit.
        
        full_tableau = stim.Tableau(len(s_str))
        # Apply baseline to it?
        # baseline instructions might refer to qubits up to baseline.num_qubits-1.
        # This is fine as long as baseline.num_qubits <= len(s_str).
        
        # We can simulate the circuit on a Tableau of size len(s_str).
        # But simpler: use existing tableau and check if S is identity on extra qubits.
        pass

    # Better way:
    # Create a tableau of size len(stabs[0]).
    sim = stim.TableauSimulator()
    # The simulator dynamically resizes? No.
    # But we can just run the circuit on a simulator initialized with enough qubits.
    
    # We want to check preservation.
    # Preservation means: <0| U^dag S U |0> = 1.
    # Equivalently: measure S on the state U|0>. Result is deterministic +1.
    
    # So:
    # 1. Initialize simulator.
    # 2. Run baseline.
    # 3. For each stabilizer S:
    #    measure expectation of S.
    #    If +1, preserved.
    
    sim = stim.TableauSimulator()
    sim.do(baseline)
    
    preserved_count = 0
    for s_str in stabs:
        s = stim.PauliString(s_str)
        if sim.peek_observable_expectation(s) == 1:
            preserved_count += 1
            
    print(f"Preserved: {preserved_count}/{total}")
    
    # Count CX
    cx = 0
    for instr in baseline:
        if instr.name in ["CX", "CNOT"]:
            cx += len(instr.targets_copy()) // 2
    print(f"Baseline CX: {cx}")

if __name__ == "__main__":
    solve()
