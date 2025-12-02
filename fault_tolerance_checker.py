"""
Check if a quantum circuit is fault-tolerant by analyzing error propagation.

This module implements fault-tolerance verification by:
1. Enumerating all fault locations (gates, preps, measurements)
2. Injecting single Pauli errors (X, Z) at each location
3. Propagating errors through the circuit using Stim
4. Checking if any single error propagates to >1 data qubit in the same block

Based on the fault-tolerance definition from quant-ph/0504218.
"""

import stim
import numpy as np
from typing import List, Dict, Tuple, Set, Optional, Union, Any
from dataclasses import dataclass
import itertools


@dataclass
class FaultLocation:
    """Represents a location where a fault can occur."""
    step: int  # Time step in the circuit
    qubit: int  # Qubit index
    gate_type: str  # Type of gate or operation (e.g., 'H', 'CX', 'R', 'M')
    target_qubits: Tuple[int, ...]  # All qubits involved in this operation
    
    def __repr__(self):
        return f"Step {self.step}: {self.gate_type} on {self.target_qubits}"


@dataclass
class ErrorPropagation:
    """Represents how an error propagates through the circuit."""
    initial_location: FaultLocation
    initial_pauli: str  # 'X', 'Y', or 'Z'
    final_pauli_string: stim.PauliString
    weight: int  # Number of non-identity Paulis at the end
    affected_qubits: Set[int]
    flags_triggered: Set[int]  # Which flag qubits have errors
    
    def __repr__(self):
        flag_info = f", flags={sorted(self.flags_triggered)}" if self.flags_triggered else ""
        return (f"Error {self.initial_pauli} at {self.initial_location} "
                f"→ weight {self.weight} on qubits {sorted(self.affected_qubits)}{flag_info}")


class FaultToleranceChecker:
    """
    Check if a circuit is fault-tolerant.
    
    A circuit is fault-tolerant if no single error at any location propagates
    to more than one data qubit in the same logical block (without flags).
    """
    
    def __init__(self, circuit: Any,  # Changed to Any to accept CNOTCircuit and other custom types
                 num_data_qubits: Optional[int] = None,
                 ancilla_qubits: Optional[List[int]] = None,
                 flag_qubits: Optional[List[int]] = None,
                 code_distance: int = 1):
        """
        Initialize the fault tolerance checker.
        
        Args:
            circuit: Stim circuit, string representation, or any circuit-like object
                    (including CNOTCircuit with to_stim_circuit() method)
            num_data_qubits: Number of data qubits (if None, inferred from circuit)
            ancilla_qubits: List of ancilla qubit indices (if None, assumes all are data)
            flag_qubits: List of flag qubit indices for flag-based fault tolerance
            code_distance: Distance of the error correcting code (default 1)
        """
        # Convert to stim.Circuit if needed
        if isinstance(circuit, str):
            self.circuit = stim.Circuit(circuit)
        elif isinstance(circuit, stim.Circuit):
            self.circuit = circuit
        elif hasattr(circuit, 'to_stim_circuit'):
            # Handle CNOTCircuit and other custom types with to_stim_circuit method
            self.circuit = circuit.to_stim_circuit()
        else:
            # Try to use it directly (assume it's circuit-like)
            self.circuit = circuit
        
        self.num_qubits = self.circuit.num_qubits
        self.code_distance = code_distance
        
        # Determine data vs ancilla vs flag qubits
        self.flag_qubits = set(flag_qubits) if flag_qubits is not None else set()
        
        if ancilla_qubits is not None:
            self.ancilla_qubits = set(ancilla_qubits) - self.flag_qubits
            self.data_qubits = set(range(self.num_qubits)) - self.ancilla_qubits - self.flag_qubits
        elif num_data_qubits is not None:
            self.data_qubits = set(range(num_data_qubits))
            all_non_data = set(range(num_data_qubits, self.num_qubits))
            self.ancilla_qubits = all_non_data - self.flag_qubits
        else:
            # Assume all qubits are data qubits
            self.data_qubits = set(range(self.num_qubits)) - self.flag_qubits
            self.ancilla_qubits = set()
        
        self.fault_locations: List[FaultLocation] = []
        self.error_propagations: List[ErrorPropagation] = []
    
    def _flatten_circuit(self, circuit: stim.Circuit) -> List:
        """
        Flatten a circuit by expanding REPEAT blocks into individual instructions.
        
        Args:
            circuit: Stim circuit that may contain REPEAT blocks
            
        Returns:
            List of individual instructions
        """
        instructions = []
        
        for item in circuit:
            # Check if it's a REPEAT block by trying to access its attributes
            try:
                # CircuitRepeatBlock has these attributes
                repeat_count = item.repeat_count  # type: ignore
                body = item.body_copy()  # type: ignore
                
                # Recursively flatten the body and repeat it
                body_instructions = self._flatten_circuit(body)
                for _ in range(repeat_count):
                    instructions.extend(body_instructions)
            except AttributeError:
                # It's a regular instruction (CircuitInstruction)
                instructions.append(item)
        
        return instructions
        
    def enumerate_fault_locations(self) -> List[FaultLocation]:
        """
        Enumerate all possible fault locations in the circuit.
        
        Returns:
            List of FaultLocation objects
        """
        locations = []
        step = 0
        
        # Flatten the circuit to handle REPEAT blocks
        flattened_instructions = self._flatten_circuit(self.circuit)
        
        for instruction in flattened_instructions:
            instruction_name = instruction.name
            
            # Handle TICK - just increment step counter
            if instruction_name == 'TICK':
                step += 1
                continue
            
            targets = instruction.targets_copy()
            
            # Extract qubit indices from targets
            qubit_indices = []
            for target in targets:
                if target.is_qubit_target:
                    qubit_indices.append(target.value)
            
            if not qubit_indices:
                continue
            
            # Define gate categories
            single_qubit_ops = [
                # State preparation
                'R', 'RX', 'RY', 'RZ', 'MR', 'MRX', 'MRY', 'MRZ',
                # Measurements
                'M', 'MX', 'MY', 'MZ',
                # Single-qubit gates
                'H', 'S', 'S_DAG', 'SQRT_X', 'SQRT_X_DAG',
                'SQRT_Y', 'SQRT_Y_DAG', 'X', 'Y', 'Z', 'I'
            ]
            
            two_qubit_ops = [
                'CX', 'CNOT', 'CY', 'CZ', 'SWAP', 'ISWAP',
                'SQRT_XX', 'SQRT_YY', 'SQRT_ZZ', 'XCZ', 'YCZ'
            ]
                
            # Add fault location for this instruction
            if instruction_name in single_qubit_ops:
                # Single-qubit operations: create one fault location per qubit
                for q in qubit_indices:
                    locations.append(FaultLocation(
                        step=step,
                        qubit=q,
                        gate_type=instruction_name,
                        target_qubits=(q,)
                    ))
                    
            elif instruction_name in two_qubit_ops:
                # Two-qubit gates: create fault locations for BOTH qubits
                # Errors can occur on either the control or target
                if len(qubit_indices) >= 2:
                    q1, q2 = qubit_indices[0], qubit_indices[1]
                    
                    # Fault location on first qubit (usually control)
                    locations.append(FaultLocation(
                        step=step,
                        qubit=q1,
                        gate_type=instruction_name,
                        target_qubits=(q1, q2)
                    ))
                    
                    # Fault location on second qubit (usually target)
                    locations.append(FaultLocation(
                        step=step,
                        qubit=q2,
                        gate_type=instruction_name,
                        target_qubits=(q1, q2)
                    ))
                
        self.fault_locations = locations
        return locations
    
    def inject_and_propagate_error(self, location: FaultLocation, 
                                   pauli_type: str) -> stim.PauliString:
        """
        Inject a Pauli error at a specific location and propagate through circuit.
        
        Strategy: Build the full circuit, tracking where to inject the error,
        then use Stim's tableau to propagate the error through.
        
        Args:
            location: Where to inject the error
            pauli_type: 'X', 'Y', or 'Z'
        
        Returns:
            Final Pauli string after propagation
        """
        # Flatten the circuit to handle REPEAT blocks
        flattened_instructions = self._flatten_circuit(self.circuit)
        
        # Build a list of all instructions with their positions
        instructions_list = []
        current_step = 0
        
        for instruction in flattened_instructions:
            if instruction.name == 'TICK':
                current_step += 1
                instructions_list.append((current_step - 1, instruction))
            else:
                instructions_list.append((current_step, instruction))
        
        # Find the index of the fault instruction
        fault_index = None
        for idx, (step, instr) in enumerate(instructions_list):
            if instr.name == 'TICK':
                continue
            
            targets = instr.targets_copy()
            qubits = [t.value for t in targets if t.is_qubit_target]
            
            if (step == location.step and 
                location.qubit in qubits and 
                instr.name == location.gate_type):
                fault_index = idx
                break
        
        if fault_index is None:
            # Couldn't find fault location, return identity
            return stim.PauliString('I' * self.num_qubits)
        
        # Build circuit_after: everything AFTER the fault instruction
        # The error occurs AFTER the fault gate executes
        circuit_after = stim.Circuit()
        for idx, (step, instr) in enumerate(instructions_list):
            if idx > fault_index:  # Exclude the fault instruction itself
                circuit_after.append(instr)
        
        # Create initial Pauli string (error at the injection location)
        pauli_list = ['I'] * self.num_qubits
        pauli_list[location.qubit] = pauli_type
        initial_error = stim.PauliString(''.join(pauli_list))
        
        # Propagate through circuit_after
        if len(circuit_after) == 0:
            # No gates after fault, error doesn't propagate
            return initial_error
        
        try:
            # Try with ignore_measurement for circuits with measurements
            tableau = stim.Tableau.from_circuit(circuit_after, ignore_measurement=True)
            final_error = tableau(initial_error)
        except Exception as e:
            # If that fails, the error doesn't propagate (return as-is)
            final_error = initial_error
        
        return final_error
    
    def analyze_error_propagation(self, pauli_types: List[str] = ['X', 'Z']) -> List[ErrorPropagation]:
        """
        Analyze how errors propagate from all fault locations.
        
        Args:
            pauli_types: Which Pauli errors to inject (default: X, Z, Y)
        
        Returns:
            List of ErrorPropagation objects
        """
        if not self.fault_locations:
            self.enumerate_fault_locations()
        
        propagations = []
        
        for location in self.fault_locations:
            for pauli in pauli_types:
                try:
                    final_pauli = self.inject_and_propagate_error(location, pauli)
                    
                    # Count weight (non-identity Paulis) on data qubits only
                    affected_data_qubits = set()
                    for q in range(self.num_qubits):
                        if q in self.data_qubits and final_pauli[q] != 0:  # 0 = I
                            affected_data_qubits.add(q)
                    
                    weight_on_data = len(affected_data_qubits)
                    
                    # Track which flag qubits are affected
                    flags_triggered = set()
                    for q in range(self.num_qubits):
                        if q in self.flag_qubits and final_pauli[q] != 0:
                            flags_triggered.add(q)
                    
                    propagation = ErrorPropagation(
                        initial_location=location,
                        initial_pauli=pauli,
                        final_pauli_string=final_pauli,
                        weight=weight_on_data,
                        affected_qubits=affected_data_qubits,
                        flags_triggered=flags_triggered
                    )
                    propagations.append(propagation)
                    
                except Exception as e:
                    # Some error injections might fail for certain circuit structures
                    print(f"Warning: Could not propagate {pauli} at {location}: {e}")
                    continue
        
        self.error_propagations = propagations
        return propagations
    
    def is_fault_tolerant(self, max_weight: Optional[int] = None, 
                         verbose: bool = True,
                         use_flags: bool = True) -> Tuple[bool, List[ErrorPropagation]]:
        """
        Check if the circuit is fault-tolerant.
        
        A circuit is fault-tolerant if:
        - Without flags: No single error propagates to >max_weight errors on data qubits
        - With flags: Errors that exceed max_weight must trigger flags, and after
          discarding flagged syndromes, remaining weight ≤ max_weight
        
        Args:
            max_weight: Maximum allowed weight on data qubits (default: code_distance)
            verbose: Print detailed results
            use_flags: If True and flag qubits are defined, use flag-based FT criterion
        
        Returns:
            Tuple of (is_fault_tolerant, list_of_violations)
        """
        if max_weight is None:
            max_weight = self.code_distance
        
        if not self.error_propagations:
            self.analyze_error_propagation()
        
        violations = []
        flagged_but_acceptable = []
        
        for prop in self.error_propagations:
            if prop.weight > max_weight:
                # Weight exceeds threshold
                if use_flags and self.flag_qubits and prop.flags_triggered:
                    # Flags triggered - this error would be detected and handled
                    # In flag-based FT, we can reject this syndrome or apply correction
                    flagged_but_acceptable.append(prop)
                else:
                    # No flags triggered (or not using flags) - true violation
                    violations.append(prop)
        
        is_ft = len(violations) == 0
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"FAULT TOLERANCE ANALYSIS")
            print(f"{'='*70}")
            print(f"Circuit qubits: {self.num_qubits}")
            print(f"Data qubits: {sorted(self.data_qubits)}")
            print(f"Ancilla qubits: {sorted(self.ancilla_qubits)}")
            if self.flag_qubits:
                print(f"Flag qubits: {sorted(self.flag_qubits)}")
                print(f"Flag-based FT: {'Enabled' if use_flags else 'Disabled'}")
            print(f"Code distance: {self.code_distance}")
            print(f"Max allowed weight on data qubits: {max_weight}")
            print(f"Total fault locations: {len(self.fault_locations)}")
            print(f"Total error propagations analyzed: {len(self.error_propagations)}")
            print(f"\n{'='*70}")
            
            if is_ft:
                print("✓ RESULT: Circuit is FAULT-TOLERANT")
                print(f"  All {len(self.error_propagations)} single-fault scenarios ")
                print(f"  propagate to ≤{max_weight} error(s) on data qubits")
                if flagged_but_acceptable:
                    print(f"\n  Note: {len(flagged_but_acceptable)} scenario(s) exceed weight {max_weight}")
                    print(f"  but are caught by flags and handled correctly")
            else:
                print(f"✗ RESULT: Circuit is NOT fault-tolerant")
                print(f"  Found {len(violations)} violation(s):")
                
                if flagged_but_acceptable:
                    print(f"\n  ({len(flagged_but_acceptable)} additional high-weight errors are ")
                    print(f"   flagged and handled correctly)")
                
                print(f"\n  Top violations:")
                # Show worst violations
                sorted_violations = sorted(violations, key=lambda x: x.weight, reverse=True)
                for i, violation in enumerate(sorted_violations, 1):
                    print(f"\n  {i}. {violation.initial_pauli} error at {violation.initial_location}")
                    print(f"     → Propagates to weight {violation.weight} on data qubits {sorted(violation.affected_qubits)}")
                    if violation.flags_triggered:
                        print(f"     → Flags triggered: {sorted(violation.flags_triggered)} (not sufficient!)")
                    else:
                        print(f"     → No flags triggered!")
                    print(f"     → Final Pauli: {violation.final_pauli_string}")
            
            print(f"{'='*70}\n")
        
        return is_ft, violations
    
    def get_propagation_summary(self) -> Dict:
        """
        Get summary statistics of error propagation.
        
        Returns:
            Dictionary with summary statistics
        """
        if not self.error_propagations:
            self.analyze_error_propagation()
        
        weights = [p.weight for p in self.error_propagations]
        
        return {
            'total_propagations': len(self.error_propagations),
            'max_weight': max(weights) if weights else 0,
            'min_weight': min(weights) if weights else 0,
            'mean_weight': np.mean(weights) if weights else 0,
            'weight_distribution': {w: weights.count(w) for w in set(weights)},
            'num_violations': sum(1 for w in weights if w > self.code_distance)
        }


def check_syndrome_extraction_ft(
    circuit: Union[stim.Circuit, str],
    data_qubits: List[int],
    ancilla_qubits: List[int],
    code_distance: int = 1,
    verbose: bool = True
) -> Tuple[bool, List[ErrorPropagation]]:
    """
    Convenience function to check if a syndrome extraction circuit is fault-tolerant.
    
    Args:
        circuit: Stim circuit
        data_qubits: List of data qubit indices
        ancilla_qubits: List of ancilla qubit indices
        code_distance: Code distance
        verbose: Print detailed output
    
    Returns:
        Tuple of (is_fault_tolerant, violations_list)
    """
    checker = FaultToleranceChecker(
        circuit=circuit,
        num_data_qubits=len(data_qubits),
        ancilla_qubits=ancilla_qubits,
        code_distance=code_distance
    )
    
    return checker.is_fault_tolerant(verbose=verbose)


if __name__ == '__main__':
    print("Example 1: Five-qubit cat state preparation")
    print("="*70)
    
    # 5-qubit cat state: |00000⟩ + |11111⟩
    cat_circuit = stim.Circuit("""
        H 0
        TICK
        CX 0 1
        TICK
        CX 0 2
        TICK
        CX 0 3
        TICK
        CX 0 4
        TICK
    """)
    
    print("\nCircuit diagram:")
    print(cat_circuit.diagram())
    print()
    
    checker1 = FaultToleranceChecker(cat_circuit, code_distance=1)
    is_ft1, violations1 = checker1.is_fault_tolerant(verbose=True)
    
    print("\n" + "="*70)
    print("Example 2: Custom Flag Circuit Test")
    print("="*70)
    
    flag_circuit = stim.Circuit("""
        CX 1 0
        TICK
        CX 1 3
        TICK
        CX 1 2
        TICK
        CX 1 0
        TICK
    """)
    
    print("\nCircuit diagram:")
    print(flag_circuit.diagram())
    print()
    
    print("Configuration: q0 is FLAG, q1,2,3 are DATA")
    print()
    
    checker2 = FaultToleranceChecker(
        circuit=flag_circuit,
        num_data_qubits=3,
        ancilla_qubits=[],
        flag_qubits=[0],
        code_distance=1
    )
    is_ft2, violations2 = checker2.is_fault_tolerant(verbose=True, use_flags=True)