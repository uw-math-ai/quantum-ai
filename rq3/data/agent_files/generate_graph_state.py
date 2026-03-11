
import stim
import sys

def main():
    try:
        # Read stabilizers
        with open("current_target_stabilizers.txt", "r") as f:
            stabilizer_lines = [line.strip() for line in f if line.strip()]

        # Parse stabilizers to a Tableau
        # Stim's Tableau.from_stabilizers expects a list of Pauli strings
        # But wait, does it handle underconstrained systems?
        # The prompt says "Target stabilizers (must all be preserved)".
        # There are 90 stabilizers for 92 qubits. It is underconstrained (2 logical qubits / degrees of freedom).
        # stim.Tableau.from_stabilizers creates a full tableau (N stabilizers for N qubits).
        # If I provide fewer, I might need to pad them or use a different method.
        
        # However, for optimization, if I find a state that stabilizes these 90, 
        # any extension to 92 is a valid stabilizer state that subsumes the 90.
        # But `evaluate_optimization` checks if the *target* stabilizers are preserved.
        # So I just need to find *any* state that stabilizes these 90.
        # I can pad with 'Z' or 'I' on the remaining degrees of freedom if needed, 
        # or just let Stim handle it if it supports it.
        
        # Actually, let's try to find a full set of stabilizers if possible, or just pick an arbitrary completion.
        # Or better, just use the 90 stabilizers and see if Stim can work with it.
        # Tableau.from_stabilizers requires N stabilizers for N qubits.
        
        # Let's verify independence first.
        
        # Create a tableau from the stabilizers by padding dummy stabilizers?
        # No, let's try to just use what we have.
        
        stabilizers = [stim.PauliString(s) for s in stabilizer_lines]
        num_qubits = len(stabilizers[0])
        print(f"Num qubits: {num_qubits}")
        print(f"Num stabilizers: {len(stabilizers)}")
        
        # Verify they commute
        for i in range(len(stabilizers)):
            for j in range(i+1, len(stabilizers)):
                if not stabilizers[i].commutes(stabilizers[j]):
                    print(f"Error: Stabilizers {i} and {j} do not commute!")
                    return

        # We need N stabilizers. We have 90, need 92.
        # We can just fill the rest with arbitrary Pauli strings that commute with existing ones.
        # But manually finding them is hard.
        # Actually, I can use Gaussian elimination to check rank and find generators.
        # But Stim doesn't have a direct "complete this set" function exposed easily in Python (maybe it does?).
        
        # Workaround: Use TableauSimulator to measure the stabilizers.
        # Start with a random state or |00...0>. Measure all 90 stabilizers.
        # The resulting state will be stabilized by them (if consistent).
        # Then extract the tableau from the simulator.
        
        sim = stim.TableauSimulator()
        # The default state is |0...0>, stabilized by Z...Z.
        # If I measure the target stabilizers, I project into their +1 eigenspace.
        # Note: if a measurement result is -1, I can apply a Pauli correction (X or Z) to flip it to +1.
        # But since I want to design a circuit that prepares +1 eigenstates,
        # I can just pretend the result was +1 or correct for it in the synthesis.
        
        # Actually, simpler:
        # 1. Start with |0...0>
        # 2. "Force" the stabilizers? No.
        
        # Better approach:
        # Create a Tableau from the stabilizers. 
        # Since I have 90, I can try to use `stim.Tableau.from_stabilizers` with a list of length 92,
        # by adding dummy 'I...I' stabilizers? No, they must be independent Pauli strings.
        
        # Let's try to find 2 more stabilizers.
        # Or, just use `stim.TableauSimulator`.
        
        sim = stim.TableauSimulator()
        # Start with |0> state (stabilizers Z0, Z1, ... Z91)
        
        # We want to reach a state stabilized by S1...S90.
        # We can assume the last 2 stabilizers are Z90 and Z91 (if independent) or whatever.
        
        # Actually, `stim.Tableau.from_stabilizers` raises an error if len != num_qubits.
        # Let's try to construct a partial tableau?
        
        # Let's blindly try to add Z on unused qubits?
        # Wait, the stabilizers are 92 chars long.
        
        # Let's try to determine which qubits are "free".
        
        # Alternative: Use the provided `generate_candidates_fresh.py` or similar if available?
        # No, I should write my own logic.
        
        # Let's use `stim.TableauSimulator` to find a valid tableau.
        # 1. Initialize sim.
        # 2. Measure each of the 90 stabilizers.
        # 3. If any measurement is -1, record it.
        # 4. At the end, we have a state that stabilizes ±S1, ±S2...
        # 5. We want +S1...
        # 6. We can fix the signs by applying gates at the end.
        # 7. Then convert the simulator's current state (Tableau) to a circuit using `to_circuit(method="graph_state")`.
        
        sim = stim.TableauSimulator()
        
        # Measure stabilizers
        # Note: sim.measure_observable(pauli_string) returns the result.
        # But this doesn't collapse the state if it commutes with current stabilizers?
        # Actually, if the stabilizer commutes with current stabilizers, it's deterministic.
        # If it anticommutes, it randomizes a pair and updates the state.
        
        # But wait, `measure_observable` is non-destructive? No, it's a measurement.
        # Wait, `measure_observable` documentation says "Returns the result of measuring... without perturbing the state if the result is deterministic."
        # If it's random, does it perturb?
        # `peek_observable_expectation` is non-perturbing.
        # `measure_observable` IS perturbing if random.
        
        # So:
        for s in stabilizers:
            sim.measure_observable(s)
            
        # Now sim is in a state stabilized by ±S_i.
        # Let's check the signs.
        corrections = []
        for i, s in enumerate(stabilizers):
            res = sim.peek_observable_expectation(s)
            if res == -1:
                # We need to flip the sign of this stabilizer.
                # But we can't easily flip just one without affecting others?
                # Actually, if we generate a circuit for this state, it prepares the state with some signs.
                # We can correct the signs later?
                # Or just hope `to_circuit` handles it?
                pass
            elif res == 0:
                # This shouldn't happen if we just measured it?
                # Unless it's dependent on previous ones (which would mean redundant stabilizers).
                print(f"Warning: Stabilizer {i} expectation is 0 after measurement.")
                
        # Get the tableau
        current_tableau = sim.current_inverse_tableau() ** -1
        
        # Synthesize circuit
        # method="graph_state" is usually best for CZ counts.
        # It produces H, S, CZ, maybe some single qubit Cliffords.
        circuit = current_tableau.to_circuit(method="graph_state")
        
        # Now we need to ensure the signs are correct.
        # The synthesized circuit `C` produces state `|psi>`.
        # `|psi>` is stabilized by `T(Z_i)`.
        # We need to check if `T(Z_i)` matches our target stabilizers `S_j`.
        # The generated circuit prepares the tableau's stabilizers.
        # But the tableau's stabilizers are what we have in the simulator.
        # The simulator state has stabilizers ±S_i (and some others for the extra degrees of freedom).
        
        # If `measure_observable` collapsed the state to -1, the circuit will prepare -1.
        # We want +1.
        # We can add X/Z gates at the START (before circuit) or END (after circuit) to fix signs?
        # The circuit maps |0> to |psi>.
        # If we flip the input bits from |0> to |1> (apply X) for the generators that correspond to -1 stabilizers, we fix the sign.
        # But we don't know which input Z_k maps to which output S_j.
        
        # Actually, `to_circuit` produces a unitary U such that U |0> = |psi>.
        # If we want to flip the sign of a stabilizer S, and S = U Z_k U^dag, then U X_k |0> = U X_k U^dag U |0> ? No.
        # If S |psi> = -|psi>, we want S |psi'> = +|psi'>.
        # If we apply an operation P such that P S P^dag = -S ? No.
        # We just want the eigenstate with +1.
        # If S = U Z_k U^-1, then Z_k corresponds to S.
        # |psi> = U |0...0>. S |psi> = U Z_k U^-1 U |0> = U Z_k |0> = U (+1)|0> = |psi>.
        # So U preserves the sign.
        # Wait, if the simulator state has expectation -1, then S |sim_state> = -|sim_state>.
        # This means the simulator state corresponds to Z_k = -1 (i.e. input was |1>).
        # But `to_circuit` generates a circuit that implements the tableau U.
        # The tableau U is defined by U Z_k U^-1 = S_k.
        # The signs are encoded in the tableau (phases).
        # So `to_circuit` SHOULD produce a circuit that prepares the exact stabilizers in the tableau (including signs).
        # BUT `to_circuit` assumes input |0...0>.
        # If the tableau has destabilizers or stabilizers with negative signs, does it handle it?
        # "The returned circuit will prepare the state stabilized by the tableau's stabilizers."
        # Does it assume the tableau stabilizers have +1 phase?
        # Stim's Tableau represents a Clifford operation.
        # The stabilizers of the output state are the image of Z_i under the operation.
        # If the image has a negative sign, e.g. Z_0 -> -X_0, then the state is stabilized by -X_0.
        # We want +X_0.
        # So we need to compose with a Pauli gate that flips the sign?
        # Or, we can iterate through the stabilizers of the tableau produced by the simulator.
        # If we find -S_i, we need to apply a correction.
        
        # Actually, the simplest way is:
        # 1. Get the circuit.
        # 2. Prepend X gates on qubits where the corresponding stabilizer has a negative sign?
        # No, "graph_state" decomposition creates a circuit C.
        # C |0> = |psi>.
        # Stabilizers of |psi> are C Z_i C^-1.
        # We need to verify if these match our targets.
        
        # Let's write the candidate to a file and check it with `evaluate_optimization`.
        # If it fails validity, we can try to fix signs.
        
        with open("candidate_graph.stim", "w") as f:
            f.write(str(circuit))
            
        print("Generated candidate_graph.stim")
        
        # Count CZs
        cz_count = sum(1 for op in circuit if op.name == "CZ")
        cx_count = sum(1 for op in circuit if op.name == "CX")
        print(f"CZ count: {cz_count}")
        print(f"CX count: {cx_count}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
