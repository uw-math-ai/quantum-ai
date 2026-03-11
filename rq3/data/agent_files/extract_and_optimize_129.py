import stim

def solve():
    # Load baseline
    try:
        baseline = stim.Circuit.from_file("baseline_129.stim")
    except Exception as e:
        print(f"Error loading baseline: {e}")
        return

    # Simulate to get stabilizers
    sim = stim.TableauSimulator()
    sim.do(baseline)
    
    # We want to synthesize a circuit that produces the same state (up to global phase).
    # The state is uniquely defined by its stabilizers.
    # canon_stabilizers returns a list of PauliString.
    stabilizers = sim.canonical_stabilizers()
    
    # Now synthesize from these stabilizers
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        circuit = tableau.to_circuit(method="graph_state")
        
        def target_str(t):
            if t.is_x_target: return f"X{t.value}"
            if t.is_y_target: return f"Y{t.value}"
            if t.is_z_target: return f"Z{t.value}"
            return str(t.value)

        # Write directly to file to avoid Stim's auto-merging
        with open("candidate_129.stim", "w") as f:
            for instruction in circuit:
                name = instruction.name
                targets = instruction.targets_copy()
                
                if name in ["R", "RZ"]:
                    continue
                elif name == "RX":
                    # RX becomes H
                    for t in targets:
                        f.write(f"H {target_str(t)}\n")
                elif name in ["CX", "CY", "CZ", "XCX", "XCY", "XCZ", "YCX", "YCY", "YCZ"]:
                    # 2-qubit gates
                    for i in range(0, len(targets), 2):
                        f.write(f"{name} {target_str(targets[i])} {target_str(targets[i+1])}\n")
                elif name in ["H", "S", "S_DAG", "X", "Y", "Z", "I", "SQRT_X", "SQRT_Y", "SQRT_Z", "SQRT_X_DAG", "SQRT_Y_DAG", "SQRT_Z_DAG"]:
                    # 1-qubit gates
                    for t in targets:
                        f.write(f"{name} {target_str(t)}\n")
                elif name == "TICK":
                    f.write("TICK\n")
                else:
                    # Other gates
                    f.write(str(instruction) + "\n")
                    
        print("Candidate written to candidate_129.stim")
        
    except Exception as e:
        print(f"Error synthesizing: {e}")

if __name__ == "__main__":
    solve()
