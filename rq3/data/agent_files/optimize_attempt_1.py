import stim

def load_circuit(filename):
    with open(filename, 'r') as f:
        return stim.Circuit(f.read())

def get_metrics(circuit):
    cx_count = sum(1 for op in circuit.flattened() if op.name == 'CX')
    volume = len(list(circuit.flattened()))
    return cx_count, volume

def main():
    baseline = load_circuit('current_task_baseline.stim')
    print("Baseline metrics:", get_metrics(baseline))
    
    tableau = stim.Tableau.from_circuit(baseline)
    
    # Method 1: Elimination
    try:
        cand_elim = tableau.to_circuit(method="elimination")
        print("Elimination metrics:", get_metrics(cand_elim))
        with open('candidate_elimination.stim', 'w') as f:
            f.write(str(cand_elim))
    except Exception as e:
        print("Elimination failed:", e)

    # Method 2: Graph State (if possible via some trick, or just check if it's better)
    # Actually, tableau.to_circuit doesn't support "graph_state".
    # But we can try to find a graph state that stabilizes the same state.
    # However, we need to preserve the specific stabilizers, which means we need to implement the specific tableau map.
    # The stabilizers are Z_i -> S_i.
    # We need a circuit U such that U |0> = |S>.
    # Wait, the problem says "Target stabilizers (must all be preserved)". 
    # This implies we just need to prepare a state stabilized by these stabilizers.
    # AND "Use the same qubit indexing as the baseline circuit".
    
    # If the task is "generate a circuit that preserves the same stabilizer behavior", it usually means
    # preparing the state stabilized by the given stabilizers.
    # OR it means implementing the unitary U such that U * P * U^dag = P for all P in Stabilizers.
    # But usually "target stabilizers" implies a state preparation task.
    # "must be a STRICT improvement of the baseline circuit while preserving the same stabilizer behavior."
    # If the baseline is a unitary that maps input to output, "stabilizer behavior" might mean the channel.
    # But the stabilizers are given as a list of Pauli strings.
    # This usually means "The output state of the circuit (when run on |0...0>) must be stabilized by these operators".
    # Let's verify this assumption. 
    # The baseline starts with H, S, CX... it looks like a state prep or a graph state circuit.
    # If it was a channel, we would need to know input/output relations.
    # The prompt says "Target stabilizers". This strongly suggests state preparation.
    
    # So, any circuit that prepares the state stabilized by {S_i} is valid.
    # We can use tableau.to_circuit(method="elimination") on the tableau *of the state*.
    # But `stim.Tableau.from_circuit(baseline)` gives the unitary tableau (Heisenberg picture).
    # If we want the state tableau, we should simulate.
    # But `tableau.to_circuit` produces a circuit that implements the unitary.
    # If the baseline circuit prepares the state from |0>, then the unitary U satisfies U|0> = |psi>.
    # So `tableau.to_circuit` will produce U' such that U' has the same action.
    # However, U' might be more complex than necessary if it also cares about what happens to |1>, |+>, etc.
    # But since we start from |0>, we only care about the first column of the tableau (or something like that)?
    # No, we care that U'|0> is the same state.
    # We don't care what U' does to other states.
    # So we have degrees of freedom!
    # We can effectively "don't care" the x_outputs for the input Z generators?
    # Actually, the simplest way is to find a tableau T such that T(Z_i) = S_i for all i?
    # No, that would be a unitary mapping Z basis to S basis.
    # If the state is stabilized by S_i, then S_i |psi> = |psi>.
    # Since Z_i |0> = |0>, we want U Z_i U^dag = S_i ? No, that's for Heisenberg.
    # If U |0> = |psi>, then S_i U |0> = U |0> => U^dag S_i U |0> = |0>.
    # So U^dag S_i U should be a Z-type operator (or stabilizes |0>).
    # Generally, we want generated stabilizers of the state to match.
    
    # Let's assume `stim.Tableau.from_circuit` captures the full unitary, which is sufficient but maybe not necessary.
    # If we only need state prep, we can optimize further.
    # But `evaluate_optimization` checks "STABILIZER PRESERVATION".
    # "simulates the circuit with a TableauSimulator to verify that every target stabilizer has expectation +1."
    # This CONFIRMS it is a state preparation task.
    # The circuit acts on |00...0>.
    
    # So we can construct a Tableau representing the *state* and then synthesize that.
    # How to get state tableau in Stim?
    # `stim.TableauSimulator` maintains the state.
    # `sim.current_inverse_tableau()` gives T^-1 such that T^-1 |psi> = |0>.
    # So T |0> = |psi>.
    # So we can run the baseline on a simulator, get the inverse tableau, invert it to get T, and then synthesize T.
    # This T will be a unitary that prepares the state.
    # And since `to_circuit` makes a unitary, this matches.
    
    sim = stim.TableauSimulator()
    sim.do(baseline)
    # The simulator state is |psi>.
    # current_inverse_tableau returns inv(T).
    # We want T.
    inv_T = sim.current_inverse_tableau()
    T = inv_T.inverse()
    
    try:
        cand_state_elim = T.to_circuit(method="elimination")
        print("State Elimination metrics:", get_metrics(cand_state_elim))
        with open('candidate_state_elim.stim', 'w') as f:
            f.write(str(cand_state_elim))
    except Exception as e:
        print("State Elimination failed:", e)

if __name__ == "__main__":
    main()
