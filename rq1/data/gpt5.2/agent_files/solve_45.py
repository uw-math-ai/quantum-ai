
import stim
import numpy as np

stabilizers = [
    "XXXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIXXXXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIXXXXXXIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXXXIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXXXIII",
    "XXXIIIXXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIXXXIIIXXXIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIXXXIIIXXXIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIXXXIIIXXXIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXIIIXXX",
    "ZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIII",
    "ZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIZIZIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIIIIII",
    "IIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZZIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIII",
    "IIIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIZIZIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIII",
    "IIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIZZIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZI",
    "IIIIIIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIZIZIIIIIIIIIIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIZIZIIIIIIIIIIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIIIIIIIII",
    "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZ",
    "XXXIIIIIIZIIZIIZIIZIIZIIZIIXXXIIIIIIIIIIIIIII",
    "IIIIIIIIIXXXIIIIIIZIIZIIZIIZIIZIIZIIXXXIIIIII",
    "XXXIIIIIIIIIIIIIIIXXXIIIIIIZIIZIIZIIZIIZIIZII",
    "ZIIZIIZIIXXXIIIIIIIIIIIIIIIXXXIIIIIIZIIZIIZII"
]

def solve():
    num_qubits = 45
    # Parse stabilizers into a Tableau
    # We need to be careful with the order and signs. The prompt says "+1 eigenstate".
    # stim.Tableau.from_stabilizers expects PauliStrings.
    
    # 1. Convert strings to stim.PauliString
    pauli_stabilizers = [stim.PauliString(s[:45]) for s in stabilizers]
    
    # 2. Check if the stabilizers are consistent and independent
    print("Stabilizer lengths after truncation:")
    for i, s in enumerate(pauli_stabilizers):
        if len(s) != 45:
            print(f"Index {i}: length {len(s)}")

    try:
        # allow_underconstrained=True because we might not have a full set of 45 stabilizers.
        # Let's count them.
        print(f"Number of stabilizers: {len(stabilizers)}")
        
        # If we have 45 stabilizers, we can try to form a full tableau.
        # But allow_underconstrained is safer.
        tableau = stim.Tableau.from_stabilizers(pauli_stabilizers, allow_underconstrained=True, allow_redundant=True)
        
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # 3. Generate the circuit
    # 'elimination' method converts the tableau into a circuit that prepares the state |0...0> -> stabilizers
    # But wait, tableau.to_circuit() usually does the inverse or something specific?
    # Actually, `stim.Tableau.from_stabilizers` creates a tableau where the stabilizers are Z_i of the output.
    # So if we want to prepare the state, we need the inverse operation of "measuring" these stabilizers?
    # No, `to_circuit("elimination")` produces a circuit that maps the all-zero state to the state described by the tableau (or vice versa? Let's check docs or experiment).
    
    # "The 'elimination' method returns a circuit that prepares the stabilizer state described by the tableau, assuming the input is the all-zero state." - This is a common understanding, let's verify.
    # Actually, `to_circuit` documentation says: "Returns a circuit that implements the tableau."
    # If the tableau represents the state, then applying it to |0> should yield the state.
    
    # Let's verify locally.
    circuit = tableau.to_circuit("elimination")
    
    # 4. Verify
    # Simulate the circuit on |00...0>
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    # Check if the state is a +1 eigenstate of all stabilizers
    all_good = True
    for s in pauli_stabilizers:
        if not sim.measure_observable(s) == 0: # 0 means +1 eigenvalue, 1 means -1
             print(f"Failed stabilizer: {s}")
             all_good = False
             # try to correct?
             # If it's -1, we might need to flip a sign in the stabilizer or the circuit? 
             # The prompt implies +1 eigenstate.
             # If `from_stabilizers` worked, it should be +1.
             
    if all_good:
        print("Verification successful!")
        print(f"Tableau qubits: {len(tableau)}")
        print(f"Circuit qubits: {circuit.num_qubits}")
        with open("circuit_45.stim", "w") as f:
            f.write(str(circuit))
        print("Circuit written to circuit_45.stim")
    else:
        print("Verification failed.")

solve()
