"""
Verify that a quantum circuit prepares a state that is stabilized by given stabilizers.

This script uses Stim's TableauSimulator to check if the state prepared by a circuit 
is an eigenstate with eigenvalue +1 for each of the provided stabilizers.

Note: This only works for stabilizer circuits (Clifford gates + measurements).
"""

import stim
from typing import List, Union, Optional


def pauli_string_to_stim(pauli_str: str, num_qubits: int) -> stim.PauliString:
    """
    Convert a Pauli string (e.g., 'XXIIXXI') to a Stim PauliString object.
    
    Args:
        pauli_str: String of 'X', 'Z', 'Y', 'I' characters
        num_qubits: Total number of qubits in the system
    
    Returns:
        Stim PauliString representing the stabilizer
    """
    # Pad with 'I' if needed
    if len(pauli_str) < num_qubits:
        pauli_str = pauli_str + 'I' * (num_qubits - len(pauli_str))
    elif len(pauli_str) > num_qubits:
        pauli_str = pauli_str[:num_qubits]
    
    # Stim accepts Pauli strings directly
    return stim.PauliString(pauli_str)


def verify_stabilizers(
    circuit: Union[stim.Circuit, str],
    stabilizers: List[str],
    verbose: bool = True
) -> bool:
    """
    Verify that the state prepared by a circuit is stabilized by the given stabilizers.
    
    Args:
        circuit: Stim Circuit or circuit string
        stabilizers: List of Pauli strings (e.g., ['XXXX', 'ZIZI'])
        verbose: If True, print detailed verification results
    
    Returns:
        True if all stabilizers stabilize the state, False otherwise
    """
    # Convert to stim.Circuit if needed
    if isinstance(circuit, str):
        try:
            circ = stim.Circuit(circuit)
        except Exception as e:
            raise ValueError(f"Could not parse circuit string: {e}")
    elif isinstance(circuit, stim.Circuit):
        circ = circuit
    elif hasattr(circuit, 'to_stim_circuit'):
        # Handle objects with to_stim_circuit method
        try:
            circ = circuit.to_stim_circuit()
        except Exception as e:
            raise ValueError(f"Could not convert circuit to Stim: {e}")
    else:
        raise TypeError(f"Unsupported circuit type: {type(circuit)}")
    
    num_qubits = circ.num_qubits
    
    if verbose:
        print(f"Circuit has {num_qubits} qubits")
        print(f"Number of stabilizers: {len(stabilizers)}")
        print(f"\nVerifying stabilizers...")
        print("=" * 60)
    
    # Create a tableau simulator and evolve the state
    sim = stim.TableauSimulator()
    sim.do(circ)
    
    all_stabilized = True
    
    for i, stab_str in enumerate(stabilizers):
        # Convert to Stim PauliString
        pauli = pauli_string_to_stim(stab_str, num_qubits)
        
        # Check expectation value (+1 or -1)
        expectation = sim.peek_observable_expectation(pauli)
        is_stabilized = (expectation > 0)  # +1 eigenvalue
        
        if verbose:
            status = "✓" if is_stabilized else "✗"
            eigenvalue = "+1" if expectation > 0 else "-1"
            print(f"{status} Stabilizer {i+1}: {stab_str}")
            if not is_stabilized:
                print(f"    Eigenvalue: {eigenvalue} (expected: +1)")
        
        if not is_stabilized:
            all_stabilized = False
    
    if verbose:
        print("=" * 60)
        if all_stabilized:
            print("✓ SUCCESS: All stabilizers verify correctly!")
        else:
            print("✗ FAILURE: Some stabilizers do not stabilize the state.")
    
    return all_stabilized


def verify_with_custom_tableau(
    circuit: Union[stim.Circuit, str],
    stabilizers: List[str],
    verbose: bool = True
) -> bool:
    """
    Alternative verification using tableau algebra directly.
    
    This checks if the circuit conjugates each stabilizer to itself (or a phase).
    
    Args:
        circuit: Stim Circuit or circuit string
        stabilizers: List of Pauli strings
        verbose: If True, print detailed verification results
    
    Returns:
        True if all stabilizers are preserved (up to phase), False otherwise
    """
    # Convert to stim.Circuit if needed
    if isinstance(circuit, str):
        circ = stim.Circuit(circuit)
    elif isinstance(circuit, stim.Circuit):
        circ = circuit
    elif hasattr(circuit, 'to_stim_circuit'):
        circ = circuit.to_stim_circuit()
    else:
        raise TypeError(f"Unsupported circuit type: {type(circuit)}")
    
    num_qubits = circ.num_qubits
    
    # Get the tableau for the circuit
    tableau = stim.Tableau.from_circuit(circ)
    
    if verbose:
        print(f"Circuit has {num_qubits} qubits")
        print(f"Number of stabilizers: {len(stabilizers)}")
        print(f"\nChecking stabilizer preservation through circuit...")
        print("=" * 60)
    
    all_preserved = True
    
    for i, stab_str in enumerate(stabilizers):
        pauli = pauli_string_to_stim(stab_str, num_qubits)
        
        # Transform the stabilizer through the circuit
        transformed = tableau(pauli)
        
        # Check if it's the same (up to phase)
        # Two Pauli strings are the same up to phase if they have the same X and Z support
        is_preserved = (transformed == pauli or transformed == -pauli)
        
        if verbose:
            status = "✓" if is_preserved else "✗"
            print(f"{status} Stabilizer {i+1}: {stab_str}")
            if not is_preserved:
                print(f"    Transformed to: {transformed}")
        
        if not is_preserved:
            all_preserved = False
    
    if verbose:
        print("=" * 60)
        if all_preserved:
            print("✓ SUCCESS: All stabilizers preserved by circuit!")
        else:
            print("✗ FAILURE: Some stabilizers not preserved.")
    
    return all_preserved


if __name__ == '__main__':
    print("Example 1: 4-qubit GHZ state")
    print("=" * 60)
    
    # Circuit that prepares |0000⟩ + |1111⟩
    ghz_circuit = stim.Circuit("""
        H 0
        CX 0 1
        CX 1 2
        CX 2 3
    """)
    
    # GHZ state stabilizers (corrected)
    # |0000⟩ + |1111⟩ is stabilized by XXXX and products of Z_i Z_j for adjacent pairs
    ghz_stabilizers = ['XXXX', 'ZZII', 'IZZI', 'IIZZ']
    
    result1 = verify_stabilizers(
        ghz_circuit,
        ghz_stabilizers,
        verbose=True
    )
    
    print("\n" + "=" * 60)
    print("Example 2: Bell state")
    print("=" * 60)
    
    # Bell state circuit
    bell_circuit = stim.Circuit("""
        H 0
        CX 0 1
    """)
    
    # Bell state is stabilized by XX and ZZ
    bell_stabilizers = ['XX', 'ZZ']
    
    result2 = verify_stabilizers(
        bell_circuit,
        bell_stabilizers,
        verbose=True
    )
    
    print("\n" + "=" * 60)
    print("Example 3: Three-qubit repetition code")
    print("=" * 60)
    
    # |000⟩ state - use R (reset) to explicitly initialize
    zero3_circuit = stim.Circuit("""
        R 0 1 2
    """)
    
    # Repetition code stabilizers
    rep_stabilizers = ['ZZI', 'IZZ']
    
    result3 = verify_stabilizers(
        zero3_circuit,
        rep_stabilizers,
        verbose=True
    )
    
    print("\n" + "=" * 60)
    print("Example 4: Wrong stabilizers (should fail)")
    print("=" * 60)
    
    # |000⟩ is NOT stabilized by X operators
    wrong_stabilizers = ['XXI', 'IXX']
    
    result4 = verify_stabilizers(
        zero3_circuit,  # Reuse the |000⟩ circuit from Example 3
        wrong_stabilizers,
        verbose=True
    )
    
    print("\n" + "=" * 60)
    print("Example 5: Using tableau verification")
    print("=" * 60)
    
    # Check if Bell circuit preserves XX and ZZ
    result5 = verify_with_custom_tableau(
        bell_circuit,
        bell_stabilizers,
        verbose=True
    )
    
    print("\n" + "=" * 60)
    print("Example 6: 5-qubit code stabilizers")
    print("=" * 60)
    
    # Simplified 5-qubit code preparation
    five_qubit_circuit = stim.Circuit("""
        H 0
        CX 0 1
        CX 0 2
        CX 0 3
        CX 0 4
    """)
    
    # Subset of 5-qubit code stabilizers
    five_qubit_stabilizers = [
        'XZZXI',
        'IXZZX',
        'XIXZZ',
        'ZZIZZ'
    ]
    
    result6 = verify_stabilizers(
        five_qubit_circuit,
        five_qubit_stabilizers,
        verbose=True
    )
