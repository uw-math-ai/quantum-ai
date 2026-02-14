#!/usr/bin/env python3
"""
Verification Script for Steane Code Implementation

This script verifies that all components of the Steane code implementation
are working correctly and produces the expected results.
"""

import stim
import sys


def verify_circuit_file_exists():
    """Verify that the circuit file exists."""
    try:
        with open("steane_circuit_full.stim", "r") as f:
            content = f.read()
        print("✓ Circuit file exists and is readable")
        return True
    except FileNotFoundError:
        print("✗ Circuit file not found: steane_circuit_full.stim")
        return False


def verify_circuit_loads():
    """Verify that the circuit can be loaded by Stim."""
    try:
        with open("steane_circuit_full.stim", "r") as f:
            circuit = stim.Circuit(f.read())
        print("✓ Circuit loads successfully in Stim")
        return True, circuit
    except Exception as e:
        print(f"✗ Failed to load circuit: {e}")
        return False, None


def verify_circuit_parameters(circuit):
    """Verify circuit parameters."""
    if circuit.num_qubits != 7:
        print(f"✗ Expected 7 qubits, got {circuit.num_qubits}")
        return False
    
    if len(circuit) != 5:
        print(f"✗ Expected 5 instructions, got {len(circuit)}")
        return False
    
    print(f"✓ Circuit has correct parameters (7 qubits, 5 instructions)")
    return True


def verify_stabilizer_eigenvalues(circuit):
    """Verify all stabilizer eigenvalues are +1."""
    stabilizers = [
        ("X₁ = X₀X₁X₂X₃", stim.PauliString("X0*X1*X2*X3")),
        ("X₂ = X₀X₂X₄X₆", stim.PauliString("X0*X2*X4*X6")),
        ("X₃ = X₂X₃X₄X₅", stim.PauliString("X2*X3*X4*X5")),
        ("Z₁ = Z₀Z₁Z₂Z₃", stim.PauliString("Z0*Z1*Z2*Z3")),
        ("Z₂ = Z₀Z₂Z₄Z₆", stim.PauliString("Z0*Z2*Z4*Z6")),
        ("Z₃ = Z₂Z₃Z₄Z₅", stim.PauliString("Z2*Z3*Z4*Z5")),
    ]
    
    all_correct = True
    for name, stab in stabilizers:
        sim = stim.TableauSimulator()
        sim.do(circuit)
        eigenvalue = 1 if sim.measure_observable(stab) == 0 else -1
        
        if eigenvalue != 1:
            print(f"✗ {name}: eigenvalue = {eigenvalue} (expected +1)")
            all_correct = False
    
    if all_correct:
        print(f"✓ All stabilizer eigenvalues are +1")
    
    return all_correct


def verify_logical_state(circuit):
    """Verify that circuit prepares logical |0⟩ state."""
    logical_z = stim.PauliString("Z0*Z1*Z2*Z3*Z4*Z5*Z6")
    
    sim = stim.TableauSimulator()
    sim.do(circuit)
    eigenvalue = 1 if sim.measure_observable(logical_z) == 0 else -1
    
    if eigenvalue == 1:
        print(f"✓ Circuit prepares logical |0⟩ state")
        return True
    else:
        print(f"✗ Logical Z eigenvalue = {eigenvalue} (expected +1)")
        return False


def verify_commutation_relations(circuit):
    """Verify all stabilizers commute."""
    stabilizers = [
        stim.PauliString("X0*X1*X2*X3"),
        stim.PauliString("X0*X2*X4*X6"),
        stim.PauliString("X2*X3*X4*X5"),
        stim.PauliString("Z0*Z1*Z2*Z3"),
        stim.PauliString("Z0*Z2*Z4*Z6"),
        stim.PauliString("Z2*Z3*Z4*Z5"),
    ]
    
    all_commute = True
    for i, s1 in enumerate(stabilizers):
        for j, s2 in enumerate(stabilizers):
            if i < j:
                prod1 = s1 * s2
                prod2 = s2 * s1
                if prod1 != prod2:
                    print(f"✗ {s1} does not commute with {s2}")
                    all_commute = False
    
    if all_commute:
        print(f"✓ All stabilizers commute pairwise")
    
    return all_commute


def verify_error_detection():
    """Verify error detection capabilities."""
    with open("steane_circuit_full.stim", "r") as f:
        circuit = stim.Circuit(f.read())
    
    # Test a few errors
    test_cases = [
        ("No error", ""),
        ("X₀ error", "X 0"),
        ("Z₃ error", "Z 3"),
    ]
    
    syndromes = []
    for error_name, error_op in test_cases:
        error_circuit = circuit.copy()
        if error_op:
            parts = error_op.split()
            error_circuit.append(stim.CircuitInstruction(parts[0], [int(parts[1])]))
        
        # Get syndrome
        stabilizers = [
            stim.PauliString("X0*X1*X2*X3"),
            stim.PauliString("X0*X2*X4*X6"),
            stim.PauliString("X2*X3*X4*X5"),
            stim.PauliString("Z0*Z1*Z2*Z3"),
            stim.PauliString("Z0*Z2*Z4*Z6"),
            stim.PauliString("Z2*Z3*Z4*Z5"),
        ]
        
        syndrome = []
        for stab in stabilizers:
            sim = stim.TableauSimulator()
            sim.do(error_circuit)
            eigenvalue = 1 if sim.measure_observable(stab) == 0 else -1
            syndrome.append(0 if eigenvalue == 1 else 1)
        
        syndrome_str = "".join(str(b) for b in syndrome)
        syndromes.append((error_name, syndrome_str))
    
    # Verify syndromes are different
    if len(set(s[1] for s in syndromes)) == len(syndromes):
        print(f"✓ Error detection works (all syndromes unique)")
        for name, syn in syndromes:
            print(f"    {name:20s} → {syn}")
        return True
    else:
        print(f"✗ Some errors have identical syndromes")
        return False


def main():
    """Run all verification tests."""
    print("=" * 70)
    print("Steane Code Implementation Verification")
    print("=" * 70)
    
    tests = [
        ("Circuit file exists", verify_circuit_file_exists, ()),
        ("Circuit loads in Stim", verify_circuit_loads, ()),
    ]
    
    # Run initial tests
    all_pass = True
    circuit = None
    
    for test_name, test_func, args in tests:
        print(f"\nTest: {test_name}")
        print("-" * 70)
        try:
            if test_name == "Circuit loads in Stim":
                success, circuit = test_func(*args)
                if not success:
                    all_pass = False
            else:
                if not test_func(*args):
                    all_pass = False
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            all_pass = False
    
    if circuit is None:
        print("\n" + "=" * 70)
        print("VERIFICATION FAILED: Could not load circuit")
        print("=" * 70)
        return False
    
    # Run circuit-dependent tests
    circuit_tests = [
        ("Circuit parameters", verify_circuit_parameters, (circuit,)),
        ("Stabilizer eigenvalues", verify_stabilizer_eigenvalues, (circuit,)),
        ("Logical state verification", verify_logical_state, (circuit,)),
        ("Commutation relations", verify_commutation_relations, (circuit,)),
        ("Error detection", verify_error_detection, ()),
    ]
    
    for test_name, test_func, args in circuit_tests:
        print(f"\nTest: {test_name}")
        print("-" * 70)
        try:
            if not test_func(*args):
                all_pass = False
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            all_pass = False
    
    # Print summary
    print("\n" + "=" * 70)
    if all_pass:
        print("✓ ALL TESTS PASSED")
        print("=" * 70)
        print("\nThe Steane code circuit implementation is working correctly!")
        print("The circuit successfully prepares the logical |0⟩ state.")
        print("All stabilizers are satisfied and error detection works.")
        return True
    else:
        print("✗ SOME TESTS FAILED")
        print("=" * 70)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
