import stim

def check_consistency():
    with open(r"data\gemini-3-pro-preview\agent_files\stabilizers_102.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    paulis = [stim.PauliString(s) for s in stabilizers]
    
    try:
        # Try to create tableau without allow_underconstrained to see error message
        # But since we know it's underconstrained (98 < 102), we expect an error about that.
        # However, we want to know if there is a CONSISTENCY error.
        # To do that, we can try to add them one by one to a TableauSimulator?
        # Or just use Tableau.from_stabilizers and see if it fails with consistency error.
        
        # We know it succeeds with allow_underconstrained=True.
        # Let's try to verify if the resulting tableau actually satisfies all input stabilizers.
        
        tableau = stim.Tableau.from_stabilizers(paulis, allow_underconstrained=True)
        
        # Check each stabilizer against the tableau
        # A tableau stabilizes S if T^-1 * S * T is +Z_i or something?
        # Actually, simpler: T * |0> is the state.
        # We want S * (T * |0>) = T * |0>
        # => (T^-1 * S * T) * |0> = |0>
        # So we computed conjugated S' = T^-1 * S * T.
        # S' should stabilize |0>. This means S' should consist only of Zs and Is, and have +1 phase.
        # If S' has X or Y, it doesn't stabilize |0>.
        # If S' has - sign, it stabilizes |1> (or -|0>? No, -Z|0> = -|0> != |0>).
        
    sim = stim.TableauSimulator()
    # The tableau gives the state |psi> = T |00...0>
    # So we apply T to the simulator.
    # Note: sim.do_tableau applies T to the state.
    sim.do_tableau(tableau, [i for i in range(102)])
    
    failed_indices = []
    for i, p in enumerate(paulis):
        # We can use peek_observable_expectation
        # It returns +1, -1, or 0 (random)
        ex = sim.peek_observable_expectation(p)
        if ex != 1:
            print(f"Stabilizer {i} expectation: {ex}")
            failed_indices.append(i)
            
    if not failed_indices:
        print("All stabilizers satisfied by the Stim tableau.")
    else:
        print(f"Failed stabilizers: {failed_indices}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_consistency()
