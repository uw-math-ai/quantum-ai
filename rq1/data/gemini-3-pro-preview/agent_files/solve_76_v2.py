import stim
import sys

def solve():
    with open("stabilizers.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"Number of stabilizers: {len(lines)}")
    if not lines:
        print("No stabilizers found.")
        return

    num_qubits = len(lines[0])
    print(f"Number of qubits: {num_qubits}")

    # Check commutativity
    stabilizers = [stim.PauliString(line) for line in lines]
    
    try:
        # Create a Tableau that stabilizes the given stabilizers.
        # allow_underconstrained=True is important because we have 74 stabilizers for 76 qubits.
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        print("Tableau created successfully.")
        
        # Convert to circuit using elimination method (Gaussian elimination)
        circuit = tableau.to_circuit("elimination")
        print("Circuit generated.")
        
        with open("circuit_76.stim", "w") as f:
            for instruction in circuit:
                if isinstance(instruction, stim.CircuitInstruction):
                    name = instruction.name
                    targets = instruction.targets_copy()
                    
                    # Determine chunk size. For 2-qubit gates, it must be even.
                    # CX, CZ, SWAP take pairs.
                    # H, S, X, Z take singles.
                    
                    if name in ["CX", "CY", "CZ", "SWAP", "ISWAP", "SQRT_XX", "SQRT_YY", "SQRT_ZZ"]:
                        chunk_size = 4 # 2 pairs
                    else:
                        chunk_size = 4 # 4 singles
                        
                    for i in range(0, len(targets), chunk_size):
                        chunk = targets[i:i+chunk_size]
                        
                        # Only write instruction if there are targets
                        if not chunk:
                            continue

                        f.write(f"{name}")
                        for t in chunk:
                             # Accessing t.value is correct for GateTarget
                             # t is a GateTarget
                             if t.is_combiner:
                                 f.write(f" *")
                             elif t.is_x_target:
                                 f.write(f" X{t.value}")
                             elif t.is_y_target:
                                 f.write(f" Y{t.value}")
                             elif t.is_z_target:
                                 f.write(f" Z{t.value}")
                             elif t.is_inverted_result_target:
                                 f.write(f" !{t.value}")
                             elif t.is_measurement_record_target:
                                 f.write(f" rec[{t.value}]")
                             else:
                                 f.write(f" {t.value}")
                        f.write("\n")
                else:
                    # Repeat block or other
                    f.write(str(instruction) + "\n")
            
    except Exception as e:
        print(f"Error creating tableau: {e}")

if __name__ == "__main__":
    solve()
