#!/usr/bin/env python3
"""
Complete Steane [[7,1,3]] Quantum Error Correcting Code Implementation

This script generates the Steane code, which is one of the first quantum
error correcting codes. It is a CSS (Calderbank-Shor-Steane) code that
encodes 1 logical qubit into 7 physical qubits with distance 3 (can correct
any single-qubit error).

The code is defined by the following stabilizer generators:

X generators:
  X0 X1 X2 X3
  X0 X2 X4 X6
  X2 X3 X4 X5

Z generators:
  Z0 Z1 Z2 Z3
  Z0 Z2 Z4 Z6
  Z2 Z3 Z4 Z5

The script:
1. Verifies the stabilizer generators commute properly
2. Generates a Clifford circuit that prepares the logical |0> state
3. Verifies the circuit produces the correct eigenvalues for all generators
4. Outputs the circuit in Stim format
"""

import stim


class SteaneCode:
    """Class to represent and manipulate the Steane [[7,1,3]] code."""
    
    def __init__(self):
        """Initialize Steane code with stabilizer generators."""
        self.num_qubits = 7
        self.num_logical_qubits = 1
        self.distance = 3
        
        # Define X stabilizer generators
        self.x_stabilizers = [
            stim.PauliString("X0*X1*X2*X3"),
            stim.PauliString("X0*X2*X4*X6"),
            stim.PauliString("X2*X3*X4*X5"),
        ]
        
        # Define Z stabilizer generators
        self.z_stabilizers = [
            stim.PauliString("Z0*Z1*Z2*Z3"),
            stim.PauliString("Z0*Z2*Z4*Z6"),
            stim.PauliString("Z2*Z3*Z4*Z5"),
        ]
        
        # Logical operators
        self.logical_z = stim.PauliString("Z0*Z1*Z2*Z3*Z4*Z5*Z6")
        self.logical_x = stim.PauliString("X0*X1*X2*X3*X4*X5*X6")
    
    def get_all_stabilizers(self):
        """Return all 7 stabilizers (6 generators + logical Z)."""
        return self.x_stabilizers + self.z_stabilizers + [self.logical_z]
    
    def verify_commutation_relations(self, verbose=False):
        """
        Verify that all stabilizers commute with each other.
        Two Paulis P and Q commute iff P*Q = Q*P.
        Returns True if all commutation relations are satisfied.
        """
        all_stabs = self.get_all_stabilizers()
        all_commute = True
        
        if verbose:
            print("Checking commutation relations:")
            print("(Two Paulis commute if product is independent of order)")
        
        for i, s1 in enumerate(all_stabs):
            for j, s2 in enumerate(all_stabs):
                if i < j:
                    # Check if s1 * s2 == s2 * s1 (up to sign)
                    prod1 = s1 * s2
                    prod2 = s2 * s1
                    # They commute if the products are equal or negative of each other
                    commutes = (prod1 == prod2)
                    
                    if verbose:
                        status = "✓" if commutes else "✗"
                        print(f"  {status} {s1} with {s2}: s1*s2={prod1}, s2*s1={prod2}")
                    if not commutes:
                        all_commute = False
        
        return all_commute
    
    def generate_circuit(self):
        """
        Generate a Clifford circuit that prepares the Steane code logical |0> state.
        
        The circuit is synthesized from the stabilizer generators using Stim's
        tableau synthesis method.
        
        Returns:
            stim.Circuit: The prepared circuit
        """
        stabilizers = self.get_all_stabilizers()
        tableau = stim.Tableau.from_stabilizers(stabilizers)
        circuit = tableau.to_circuit()
        return circuit
    
    def verify_circuit(self, circuit, verbose=False):
        """
        Verify that the generated circuit produces the correct stabilizer state.
        
        Returns:
            bool: True if all stabilizers have eigenvalue +1
        """
        stabilizers = self.get_all_stabilizers()
        all_correct = True
        
        if verbose:
            print("Verifying circuit produces correct eigenvalues:")
        
        for stab in stabilizers:
            sim = stim.TableauSimulator()
            sim.do(circuit)
            result = sim.measure_observable(stab)
            eigenvalue = 1 if result == 0 else -1
            
            is_correct = eigenvalue == 1
            if verbose:
                status = "✓" if is_correct else "✗"
                print(f"  {status} {stab}: eigenvalue = +{eigenvalue}")
            
            if not is_correct:
                all_correct = False
        
        return all_correct
    
    def print_info(self):
        """Print information about the Steane code."""
        print("=" * 70)
        print("Steane [[7,1,3]] Quantum Error Correcting Code")
        print("=" * 70)
        print(f"\nCode parameters:")
        print(f"  Number of physical qubits: {self.num_qubits}")
        print(f"  Number of logical qubits: {self.num_logical_qubits}")
        print(f"  Code distance: {self.distance}")
        print(f"  Error correction capability: 1 qubit")
        
        print(f"\nX stabilizer generators:")
        for i, stab in enumerate(self.x_stabilizers, 1):
            print(f"  S{i}_X: {stab}")
        
        print(f"\nZ stabilizer generators:")
        for i, stab in enumerate(self.z_stabilizers, 1):
            print(f"  S{i}_Z: {stab}")
        
        print(f"\nLogical operators:")
        print(f"  Logical Z: {self.logical_z}")
        print(f"  Logical X: {self.logical_x}")


def main():
    """Main function to generate and verify Steane code circuit."""
    
    # Create Steane code instance
    steane = SteaneCode()
    steane.print_info()
    
    # Verify commutation relations
    print("\n" + "=" * 70)
    print("Step 1: Verifying Stabilizer Commutation Relations")
    print("=" * 70)
    commute_ok = steane.verify_commutation_relations(verbose=True)
    print(f"\nAll generators commute: {commute_ok}")
    
    if not commute_ok:
        print("ERROR: Not all generators commute!")
        return
    
    # Generate circuit
    print("\n" + "=" * 70)
    print("Step 2: Generating Preparation Circuit")
    print("=" * 70)
    circuit = steane.generate_circuit()
    
    print("\nGenerated circuit:")
    print(circuit)
    
    # Count operations
    cx_count = sum(1 for instr in circuit if instr.name == "CX")
    h_count = sum(1 for instr in circuit if instr.name == "H")
    
    print(f"\nCircuit statistics:")
    print(f"  Total instructions: {len(circuit)}")
    print(f"  CX gates: {cx_count}")
    print(f"  H gates: {h_count}")
    
    # Verify circuit
    print("\n" + "=" * 70)
    print("Step 3: Verifying Circuit")
    print("=" * 70)
    circuit_ok = steane.verify_circuit(circuit, verbose=True)
    print(f"\nCircuit verification: {'PASSED' if circuit_ok else 'FAILED'}")
    
    # Save circuit
    output_file = "steane_circuit_full.stim"
    with open(output_file, "w") as f:
        f.write(str(circuit))
    print(f"\nCircuit saved to {output_file}")
    
    # Print circuit in readable format
    print("\n" + "=" * 70)
    print("Circuit Operations (in order):")
    print("=" * 70)
    for i, instr in enumerate(circuit, 1):
        print(f"  {i}. {instr}")


if __name__ == "__main__":
    main()
