#!/usr/bin/env python3
"""
Simple validate_circuit implementation for the baseline_input.json
"""
import json
import sys
import os

def validate_circuit(circuit_str, stabilizers, data_qubits, flag_qubits):
    """
    Validate a quantum circuit against stabilizers.
    
    Args:
        circuit_str: STIM circuit as string
        stabilizers: List of stabilizer strings (Pauli strings)
        data_qubits: List of data qubit indices
        flag_qubits: List of flag qubit indices
        
    Returns:
        Dictionary with validation results
    """
    try:
        import stim
    except ImportError:
        print("ERROR: stim library not found. Please install it with: pip install stim")
        return {"error": "stim library not found"}
    
    result = {
        "circuit_lines": 0,
        "num_gates": 0,
        "num_qubits": 0,
        "num_data_qubits": len(data_qubits),
        "num_flag_qubits": len(flag_qubits),
        "num_stabilizers": len(stabilizers),
        "preserved_stabilizers": 0,
        "broken_stabilizers": 0,
        "broken_indices": [],
        "fault_tolerant": False,
        "data_weight_errors": [],
        "flag_weight_errors": []
    }
    
    try:
        # Parse circuit
        circuit = stim.Circuit(circuit_str)
        result["circuit_lines"] = len(circuit_str.split('\n'))
        result["num_gates"] = len(list(circuit))
        result["num_qubits"] = circuit.num_qubits
        
        # Parse stabilizers
        stabilizers_parsed = [stim.PauliString(s) for s in stabilizers]
        
        # Check if stabilizers are preserved by running circuit
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        for i, stab in enumerate(stabilizers_parsed):
            try:
                # Check if stabilizer is preserved
                expectation = sim.peek_observable_expectation(stab)
                if expectation == 1:
                    result["preserved_stabilizers"] += 1
                else:
                    result["broken_stabilizers"] += 1
                    result["broken_indices"].append(i)
            except Exception as e:
                result["broken_stabilizers"] += 1
                result["broken_indices"].append(i)
        
        # Determine if circuit is fault-tolerant
        result["fault_tolerant"] = (result["preserved_stabilizers"] == len(stabilizers))
        
        # Analyze error propagation (sample some gates)
        error_propagation = []
        gates = list(circuit)
        
        # Sample gates for error analysis (sample every 10th gate or up to 10 gates)
        sample_size = min(10, len(gates))
        sample_indices = [i * len(gates) // sample_size for i in range(sample_size)]
        
        for gate_idx in sample_indices:
            if gate_idx >= len(gates):
                break
                
            instruction = gates[gate_idx]
            gate_name = instruction.name
            targets = instruction.targets_copy()
            qubits = [t.value for t in targets if hasattr(t, 'value') and isinstance(t.value, int)]
            
            if not qubits or gate_name not in ["CX", "H"]:
                continue
            
            # Try to inject X or Z on first qubit
            for pauli_type in ["X", "Z"]:
                try:
                    # Build remaining circuit
                    remaining = stim.Circuit()
                    for k in range(gate_idx + 1, len(gates)):
                        remaining.append(gates[k])
                    
                    # Create tableau for propagation
                    t = stim.Tableau(circuit.num_qubits)
                    t.do(remaining)
                    
                    # Inject error
                    error_pauli = stim.PauliString(circuit.num_qubits)
                    error_pauli[qubits[0]] = pauli_type
                    
                    # Propagate error
                    final_pauli = t(error_pauli)
                    
                    # Count weight on data vs flag qubits
                    data_weight = sum(1 for q in data_qubits if final_pauli[q] != 'I')
                    flag_weight = sum(1 for q in flag_qubits if final_pauli[q] != 'I')
                    
                    error_propagation.append({
                        "gate_index": gate_idx,
                        "gate": gate_name,
                        "fault_qubit": qubits[0],
                        "fault_pauli": pauli_type,
                        "data_weight": data_weight,
                        "flag_weight": flag_weight
                    })
                except Exception as e:
                    pass
        
        result["error_propagation"] = error_propagation
        
    except Exception as e:
        result["error"] = str(e)
        import traceback
        result["traceback"] = traceback.format_exc()
    
    return result


def main():
    # Load the baseline input JSON
    json_file = 'data/gemini-3-pro-preview/agent_files_ft/baseline_input.json'
    
    if not os.path.exists(json_file):
        print(f"ERROR: File {json_file} not found")
        sys.exit(1)
    
    # Execute the file to get the JSON data
    with open(json_file) as f:
        code = f.read()
    
    # Execute the code to extract variables
    namespace = {}
    exec(code, namespace)
    
    circuit_str = namespace['circuit_str']
    stabilizers = namespace['stabilizers']
    data_qubits = namespace['data_qubits']
    flag_qubits = namespace['flag_qubits']
    
    print("=" * 70)
    print("VALIDATE_CIRCUIT RESULTS")
    print("=" * 70)
    
    # Run validation
    result = validate_circuit(circuit_str, stabilizers, data_qubits, flag_qubits)
    
    # Print results
    print(json.dumps(result, indent=2))
    
    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Fault-Tolerant: {result['fault_tolerant']}")
    print(f"Preserved Stabilizers: {result['preserved_stabilizers']}/{result['num_stabilizers']}")
    print(f"Broken Stabilizers: {result['broken_stabilizers']}/{result['num_stabilizers']}")
    print(f"Circuit Gates: {result['num_gates']}")
    print(f"Circuit Qubits: {result['num_qubits']}")
    print(f"Data Qubits: {result['num_data_qubits']}")
    print(f"Flag Qubits: {result['num_flag_qubits']}")
    
    if result.get('error_propagation'):
        print(f"\nError Propagation Analysis (sampled {len(result['error_propagation'])} gates):")
        max_data_weight = max((e['data_weight'] for e in result['error_propagation']), default=0)
        max_flag_weight = max((e['flag_weight'] for e in result['error_propagation']), default=0)
        print(f"  - Max data weight in sample: {max_data_weight}")
        print(f"  - Max flag weight in sample: {max_flag_weight}")


if __name__ == "__main__":
    main()
