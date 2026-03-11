import stim

def solve():
    # Hardcoded stabilizers to avoid file issues
    content = """IIXIXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIXIXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIXIXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIXIXXXIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXXXIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXXXIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXXXIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXXX, IXIXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIXIXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIXIXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIXIXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXXIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXXIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXXIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXX, XXXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIXXXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIXXXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIXXXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXIIXIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXIIXIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXIIXIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXIIXI, IIZIZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIZIZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIZIZZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIZIZZZIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZZZIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZZZIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZZZIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZZZ, IZIZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIZIZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIZIZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIZIZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZZIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZZIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZZIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZZ, ZZZIIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIZZZIIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIZZZIIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIZZZIIZIIIIIIIIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZIIZIIIIIIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZIIZIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZIIZIIIIIIII, IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZIIZI, XXIXIIIXXIXIIIXXIXIIIXXIXIIIXXIXIIIXXIXIIIXXIXIIIXXIXIII, ZZIZIIIZZIZIIIZZIZIIIZZIZIIIZZIZIIIZZIZIIIZZIZIIIZZIZIII"""
    
    # Parse comma separated list
    lines = [s.strip() for s in content.replace("\n", ",").split(",") if s.strip()]
    
    # Check num qubits
    num_qubits = len(lines[0])
    print(f"Num qubits: {num_qubits}")
    
    # Create tableau
    try:
        t = stim.Tableau.from_stabilizers([stim.PauliString(l) for l in lines])
    except Exception as e:
        print(f"Error creating tableau: {e}")
        # If stabilizers are underconstrained (fewer than N), we need to fill the rest with Z or something valid.
        # But usually 'from_stabilizers' expects a full set of N stabilizers for N qubits.
        # Let's count them.
        print(f"Number of stabilizers: {len(lines)}")
        if len(lines) < num_qubits:
             print("Underconstrained! 'from_stabilizers' usually requires N stabilizers for N qubits for a unique state.")
             # We can try allow_underconstrained=True but that creates a Tableau that might not be fully defined?
             # actually from_stabilizers returns a Tableau where the provided stabilizers are the output Z generators.
             # If < N, it pads.
             t = stim.Tableau.from_stabilizers([stim.PauliString(l) for l in lines], allow_underconstrained=True)

    # Synthesize with graph_state
    # This method produces a circuit with H, S, CZ, and potentially single qubit Cliffords.
    # It attempts to make a graph state (CZ + local Cliffords).
    circuit = t.to_circuit(method="graph_state")
    
    # We need to post-process to remove resets if any
    # RX gate is a Reset to |+> state.
    # R gate (RZ) is a Reset to |0> state.
    # Since we start in |0>, R is identity (redundant) if it's at the start.
    # RX at the start is equivalent to H (since H|0> = |+>).
    # M is measurement. We shouldn't have measurements unless necessary, but graph_state shouldn't produce M for synthesis unless requested?
    
    new_circuit = stim.Circuit()
    for instr in circuit:
        if instr.name == "R": # Reset Z
            # Ignore if at start? 
            # If it's effectively a reset, and we assume start is |0>, we can ignore it.
            # But let's check if it's used mid-circuit. 
            # 'to_circuit' usually puts initialization at the beginning.
            pass
        elif instr.name == "RX": # Reset X
            # Replace with H
            new_circuit.append("H", instr.targets_copy())
        elif instr.name == "M" or instr.name == "MX" or instr.name == "MZ":
            # Should not happen for state prep
            print(f"Warning: Measurement found: {instr}")
            new_circuit.append(instr)
        else:
            new_circuit.append(instr)
            
    # print("Generated Circuit:")
    # print(new_circuit)
    
    with open("candidate.stim", "w") as f:
        f.write(str(new_circuit))
    
    # Verify validity locally if possible?
    # We can use our own tableau simulator to check.
    sim = stim.TableauSimulator()
    sim.do_circuit(new_circuit)
    
    # Check stabilizers
    valid = True
    for s_str in lines:
        s = stim.PauliString(s_str)
        if sim.peek_observable_expectation(s) != 1:
            valid = False
            # print(f"Failed stabilizer: {s_str}")
            break
            
    if valid:
        print("\nVerified: All stabilizers preserved.")
    else:
        print("\nVerification Failed!")

if __name__ == "__main__":
    solve()
