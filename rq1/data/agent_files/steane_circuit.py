#!/usr/bin/env python3
"""
Generate a Stim circuit for the 7-qubit Steane code state.

The Steane [[7,1,3]] code is defined by:
X generators:
- X0 X1 X2 X3
- X0 X2 X4 X6
- X2 X3 X4 X5

Z generators:
- Z0 Z1 Z2 Z3
- Z0 Z2 Z4 Z6
- Z2 Z3 Z4 Z5

We prepare the logical |0> state by adding the logical Z generator
(Z on all 7 qubits) to uniquely define the state, then synthesizing
a circuit that produces this stabilizer state.
"""

import stim

def create_steane_stabilizers():
    """Create the list of 7 stabilizers for the Steane code logical |0>."""
    
    # The 3 X generators (using sparse notation X0*X1*X2*X3)
    x_gens = [
        stim.PauliString("X0*X1*X2*X3"),
        stim.PauliString("X0*X2*X4*X6"),
        stim.PauliString("X2*X3*X4*X5"),
    ]
    
    # The 3 Z generators (using sparse notation Z0*Z1*Z2*Z3)
    z_gens = [
        stim.PauliString("Z0*Z1*Z2*Z3"),
        stim.PauliString("Z0*Z2*Z4*Z6"),
        stim.PauliString("Z2*Z3*Z4*Z5"),
    ]
    
    # The logical Z operator (all Z's) - this defines the unique state
    # as the logical |0> state
    logical_z = stim.PauliString("Z0*Z1*Z2*Z3*Z4*Z5*Z6")
    
    # Verify commutation relations
    print("Verifying commutation relations:")
    all_stabilizers = x_gens + z_gens + [logical_z]
    for i, s1 in enumerate(all_stabilizers):
        for j, s2 in enumerate(all_stabilizers):
            if i < j:
                commutes = (s1 * s2).sign == 1  # Pauli strings commute if product has sign +1
                print(f"  {s1} commutes with {s2}: {commutes}")
    
    return x_gens + z_gens + [logical_z]


def create_circuit_from_stabilizers(stabilizers):
    """
    Create a Clifford circuit that produces the stabilizer state.
    
    This uses stim.Tableau.from_stabilizers to create a tableau,
    then converts it to a circuit.
    """
    
    # Create a tableau from the stabilizers
    tableau = stim.Tableau.from_stabilizers(stabilizers)
    
    # Convert the tableau to a circuit
    circuit = tableau.to_circuit()
    
    return circuit


def verify_circuit(circuit, stabilizers):
    """Verify that the circuit produces the correct stabilizer state."""
    
    print("\nVerifying circuit produces correct stabilizers:")
    
    # Create a simulator and run the circuit
    simulator = stim.TableauSimulator()
    simulator.do(circuit)
    
    # Check each stabilizer by measuring it
    for stab in stabilizers:
        # Reset simulator for each measurement
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        # Measure the observable
        result = sim.measure_observable(stab)
        eigenvalue = 1 if result == 0 else -1
        print(f"  {stab}: eigenvalue = +{eigenvalue}")


def main():
    print("=" * 70)
    print("Steane [[7,1,3]] Code - Circuit Generation")
    print("=" * 70)
    
    # Create the stabilizers
    stabilizers = create_steane_stabilizers()
    
    print("\nStabilizers:")
    for i, stab in enumerate(stabilizers, 1):
        print(f"  S{i}: {stab}")
    
    # Create the circuit
    print("\n" + "=" * 70)
    print("Generating circuit from stabilizers...")
    print("=" * 70)
    
    circuit = create_circuit_from_stabilizers(stabilizers)
    
    print("\nCircuit:")
    print(circuit)
    
    # Save the circuit to a file
    circuit_file = "steane_circuit.stim"
    with open(circuit_file, "w") as f:
        f.write(str(circuit))
    print(f"\nCircuit saved to {circuit_file}")
    
    # Verify the circuit
    print("\n" + "=" * 70)
    print("Verifying circuit...")
    print("=" * 70)
    verify_circuit(circuit, stabilizers)
    
    # Print circuit statistics
    print(f"\nCircuit statistics:")
    print(f"  Number of qubits: {circuit.num_qubits}")
    print(f"  Number of operations: {len(circuit)}")
    print(f"  Operations by type:")
    for op in circuit:
        print(f"    {op}")


if __name__ == "__main__":
    main()
