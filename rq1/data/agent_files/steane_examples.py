#!/usr/bin/env python3
"""
Practical Usage Examples for the Steane Code

This script demonstrates how to:
1. Generate the Steane code circuit
2. Simulate it with and without errors
3. Detect and analyze errors
4. Understand the code space
"""

import stim
import random


def example_1_basic_circuit():
    """Example 1: Generate and display the basic circuit."""
    print("=" * 70)
    print("Example 1: Basic Circuit Generation")
    print("=" * 70)
    
    # Create stabilizer generators
    stabilizers = [
        stim.PauliString("X0*X1*X2*X3"),
        stim.PauliString("X0*X2*X4*X6"),
        stim.PauliString("X2*X3*X4*X5"),
        stim.PauliString("Z0*Z1*Z2*Z3"),
        stim.PauliString("Z0*Z2*Z4*Z6"),
        stim.PauliString("Z2*Z3*Z4*Z5"),
        stim.PauliString("Z0*Z1*Z2*Z3*Z4*Z5*Z6"),  # Logical Z
    ]
    
    # Generate circuit from stabilizers
    tableau = stim.Tableau.from_stabilizers(stabilizers)
    circuit = tableau.to_circuit()
    
    print("\nGenerated circuit:")
    print(circuit)
    print(f"\nCircuit has {circuit.num_qubits} qubits and {len(circuit)} instructions")


def example_2_error_detection():
    """Example 2: Demonstrate error detection capabilities."""
    print("\n" + "=" * 70)
    print("Example 2: Error Detection")
    print("=" * 70)
    
    # Load the circuit
    with open("steane_circuit_full.stim", "r") as f:
        circuit = stim.Circuit(f.read())
    
    # Define stabilizers
    stabilizers = [
        ("X₁", stim.PauliString("X0*X1*X2*X3")),
        ("X₂", stim.PauliString("X0*X2*X4*X6")),
        ("X₃", stim.PauliString("X2*X3*X4*X5")),
        ("Z₁", stim.PauliString("Z0*Z1*Z2*Z3")),
        ("Z₂", stim.PauliString("Z0*Z2*Z4*Z6")),
        ("Z₃", stim.PauliString("Z2*Z3*Z4*Z5")),
    ]
    
    # Test different error locations
    test_errors = [
        ("No error", ""),
        ("X error on qubit 0", "X 0"),
        ("Z error on qubit 3", "Z 3"),
        ("Y error on qubit 6", "Y 6"),
    ]
    
    print("\nStabilizer measurement syndromes for different errors:")
    print("-" * 70)
    
    for error_name, error_op in test_errors:
        # Create circuit with error
        error_circuit = circuit.copy()
        if error_op:
            # Insert error after state preparation
            error_circuit.append(stim.CircuitInstruction(error_op.split()[0], 
                                                        [int(error_op.split()[1])]))
        
        # Measure stabilizers
        syndrome = []
        for stab_name, stab in stabilizers:
            sim = stim.TableauSimulator()
            sim.do(error_circuit)
            eigenvalue = 1 if sim.measure_observable(stab) == 0 else -1
            # Syndrome bit is 0 if eigenvalue is +1, 1 if -1
            syndrome.append(0 if eigenvalue == 1 else 1)
        
        syndrome_str = "".join(str(b) for b in syndrome)
        print(f"  {error_name:25s} → Syndrome: {syndrome_str}")


def example_3_code_space():
    """Example 3: Understanding the code space."""
    print("\n" + "=" * 70)
    print("Example 3: Code Space Structure")
    print("=" * 70)
    
    print("\nThe Steane code defines a 2-dimensional code space:")
    print("  - 6 stabilizer generators define a subspace")
    print("  - Adding logical Z gives us the logical |0⟩ state")
    print("  - The logical |1⟩ state would have logical Z eigenvalue -1")
    
    print("\nLogical basis states:")
    print("  |0_L⟩ = +1 eigenstate of logical Z")
    print("  |1_L⟩ = -1 eigenstate of logical Z")
    
    print("\nCodewords (vectors in the stabilizer code):")
    print("  A codeword is any state stabilized by all generators")
    print("  Each codeword can be described by:")
    print("    - Its eigenvalue under logical Z: ±1")
    print("    - This uniquely determines if it's |0_L⟩ or |1_L⟩")


def example_4_physical_properties():
    """Example 4: Physical properties of the code."""
    print("\n" + "=" * 70)
    print("Example 4: Physical Properties")
    print("=" * 70)
    
    print("\nSteane Code Parameters:")
    print("  [[n, k, d]] = [[7, 1, 3]]")
    print("    n = 7: Uses 7 physical qubits")
    print("    k = 1: Encodes 1 logical qubit")
    print("    d = 3: Distance 3 (corrects 1 error)")
    
    print("\nError Correction Capabilities:")
    print("  ✓ Can detect any single-qubit error")
    print("  ✓ Can correct any single-qubit error")
    print("  ✓ Cannot correct 2 simultaneous errors")
    
    print("\nThreshold Information:")
    print("  Physical error rate threshold: ~1.9%")
    print("  Below this threshold, error rates decrease exponentially with code size")
    
    print("\nComparison with other codes:")
    print("  5-qubit code: [[5,1,3]] - fewer qubits, same distance")
    print("  Golay code: [[23,1,7]] - more qubits, higher distance")
    print("  Surface code: Scalable, threshold ~1%")


def example_5_measurement_sequence():
    """Example 5: Typical measurement sequence in error correction."""
    print("\n" + "=" * 70)
    print("Example 5: Error Correction Sequence")
    print("=" * 70)
    
    print("\n1. PREPARATION PHASE:")
    print("   - Apply the preparation circuit (generated by our script)")
    print("   - Result: Logical |0⟩ state stabilized by all generators")
    
    print("\n2. STORAGE PHASE:")
    print("   - Wait time T (errors may occur)")
    print("   - With probability 7p per unit time, a single-qubit error occurs")
    print("   - With probability 21p², two-qubit errors (detected but not corrected)")
    
    print("\n3. SYNDROME EXTRACTION:")
    print("   - Measure all 6 stabilizer generators")
    print("   - Each measurement yields ±1 eigenvalue")
    print("   - 6 bits of syndrome information (1 bit per stabilizer)")
    
    print("\n4. ERROR IDENTIFICATION:")
    print("   - 7 possible single-qubit errors (X on qubits 0-6)")
    print("   - Each produces unique syndrome pattern")
    print("   - 1 pattern for 'no error' (syndrome = 0)")
    print("   - Total: 8 patterns for 7 error locations + no error")
    
    print("\n5. CORRECTION:")
    print("   - Apply appropriate correction operation")
    print("   - Removes the detected error")
    print("   - Recovers the logical state")


def example_6_load_and_run():
    """Example 6: Load and run the pre-generated circuit."""
    print("\n" + "=" * 70)
    print("Example 6: Loading and Running Pre-generated Circuit")
    print("=" * 70)
    
    try:
        with open("steane_circuit_full.stim", "r") as f:
            circuit_text = f.read()
        
        circuit = stim.Circuit(circuit_text)
        
        print(f"\n✓ Successfully loaded circuit from steane_circuit_full.stim")
        print(f"  Circuit size: {circuit.num_qubits} qubits, {len(circuit)} instructions")
        
        # Verify the state
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        print(f"\n✓ Circuit executes successfully in simulator")
        print(f"  Ready for measurement or further operations")
        
        # Show how to use it for computation
        print(f"\nUsing the circuit for error detection:")
        logical_z = stim.PauliString("Z0*Z1*Z2*Z3*Z4*Z5*Z6")
        eigenval = 1 if sim.measure_observable(logical_z) == 0 else -1
        print(f"  Logical Z eigenvalue: +{eigenval}")
        print(f"  Confirms: We have prepared the logical |0⟩ state")
        
    except FileNotFoundError:
        print("Error: Circuit file not found. Run steane_code_complete.py first.")


def main():
    """Run all examples."""
    examples = [
        example_1_basic_circuit,
        example_2_error_detection,
        example_3_code_space,
        example_4_physical_properties,
        example_5_measurement_sequence,
        example_6_load_and_run,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\nError in {example.__name__}: {e}")
    
    print("\n" + "=" * 70)
    print("All examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
