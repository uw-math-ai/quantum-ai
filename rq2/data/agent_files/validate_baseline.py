#!/usr/bin/env python3
"""
Validate the baseline circuit from input.stim and stabilizers.txt
"""
import json
import sys
import os

def parse_stim_circuit(filename):
    """Parse STIM circuit from file"""
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Filter out empty lines and comments
    circuit_lines = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            # Remove line numbers if present
            if '. ' in line:
                parts = line.split('. ', 1)
                if len(parts) == 2:
                    line = parts[1]
            circuit_lines.append(line)
    
    return '\n'.join(circuit_lines)

def parse_stabilizers(filename):
    """Parse stabilizers from text file"""
    stabilizers = []
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            # Remove line numbers if present
            if '. ' in line:
                parts = line.split('. ', 1)
                if len(parts) == 2:
                    line = parts[1]
            if line:
                stabilizers.append(line)
    
    return stabilizers

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
        "error_propagation_analysis": {}
    }
    
    try:
        # Parse circuit
        circuit = stim.Circuit(circuit_str)
        result["circuit_lines"] = len(circuit_str.split('\n'))
        result["num_gates"] = len(list(circuit))
        result["num_qubits"] = circuit.num_qubits
        
        print(f"\n[DEBUG] Circuit loaded: {result['num_qubits']} qubits, {result['num_gates']} gates")
        
        # Parse stabilizers
        stabilizers_parsed = [stim.PauliString(s) for s in stabilizers]
        
        # Check if stabilizers are preserved by running circuit
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        print(f"[DEBUG] Checking {len(stabilizers_parsed)} stabilizers...")
        
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
                print(f"[DEBUG] Error checking stabilizer {i}: {e}")
        
        print(f"[DEBUG] Preserved: {result['preserved_stabilizers']}, Broken: {result['broken_stabilizers']}")
        
        # Determine if circuit is fault-tolerant
        result["fault_tolerant"] = (result["preserved_stabilizers"] == len(stabilizers))
        
        # Analyze error propagation
        print(f"\n[DEBUG] Analyzing error propagation...")
        error_events = []
        gates = list(circuit)
        
        # Check all gates for error propagation
        for gate_idx in range(min(50, len(gates))):  # Sample first 50 gates
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
                    
                    if data_weight >= 7:  # Threshold for FT with distance 15
                        error_events.append({
                            "gate_index": gate_idx,
                            "gate": gate_name,
                            "fault_qubit": qubits[0],
                            "fault_pauli": pauli_type,
                            "data_weight": data_weight,
                            "flag_weight": flag_weight,
                            "final_pauli": str(final_pauli)
                        })
                except Exception as e:
                    pass
        
        # Sort by data weight (most severe first)
        error_events.sort(key=lambda x: x['data_weight'], reverse=True)
        
        result["critical_error_events"] = error_events[:10]  # Top 10
        result["total_critical_events"] = len(error_events)
        
        if error_events:
            print(f"[DEBUG] Found {len(error_events)} critical error propagation events (data_weight >= 7)")
            print(f"[DEBUG] Most severe: data_weight={error_events[0]['data_weight']}")
        else:
            print(f"[DEBUG] No critical error propagation events found")
        
    except Exception as e:
        result["error"] = str(e)
        import traceback
        result["traceback"] = traceback.format_exc()
        print(f"[ERROR] {e}")
        print(traceback.format_exc())
    
    return result


def main():
    # Load circuit and stabilizers from files
    circuit_file = 'data/gemini-3-pro-preview/agent_files_ft/input.stim'
    stabilizers_file = 'data/gemini-3-pro-preview/agent_files_ft/stabilizers.txt'
    
    if not os.path.exists(circuit_file):
        print(f"ERROR: File {circuit_file} not found")
        sys.exit(1)
    
    if not os.path.exists(stabilizers_file):
        print(f"ERROR: File {stabilizers_file} not found")
        sys.exit(1)
    
    print("=" * 70)
    print("BASELINE CIRCUIT VALIDATION")
    print("=" * 70)
    print(f"Loading circuit from: {circuit_file}")
    print(f"Loading stabilizers from: {stabilizers_file}")
    
    # Parse circuit and stabilizers
    circuit_str = parse_stim_circuit(circuit_file)
    stabilizers = parse_stabilizers(stabilizers_file)
    
    print(f"\n[INFO] Parsed circuit with {len(circuit_str.split(chr(10)))} lines")
    print(f"[INFO] Parsed {len(stabilizers)} stabilizers")
    
    # Code distance is 15, so FT threshold is floor((15-1)/2) = 7
    # For now, all qubits in the circuit are data qubits
    # We'll determine this after parsing the circuit
    import stim
    circuit = stim.Circuit(circuit_str)
    num_qubits = circuit.num_qubits
    data_qubits = list(range(num_qubits))
    flag_qubits = []
    
    print(f"\n[INFO] Configuration:")
    print(f"  - Code distance: 15")
    print(f"  - FT threshold: 7 (floor((15-1)/2))")
    print(f"  - Data qubits: 0-{num_qubits-1} ({num_qubits} qubits)")
    print(f"  - Flag qubits: none")
    
    print("\n" + "=" * 70)
    print("Running validation...")
    print("=" * 70)
    
    # Run validation
    result = validate_circuit(circuit_str, stabilizers, data_qubits, flag_qubits)
    
    # Print results
    print("\n" + "=" * 70)
    print("DETAILED RESULTS")
    print("=" * 70)
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
    
    if result.get('critical_error_events'):
        print(f"\nMost Severe Error Propagation Events:")
        for i, event in enumerate(result['critical_error_events'][:5], 1):
            print(f"  {i}. Gate {event['gate_index']} ({event['gate']}): "
                  f"fault on Q{event['fault_qubit']} ({event['fault_pauli']}) -> "
                  f"data_weight={event['data_weight']}")
    
    if result.get('error'):
        print(f"\nERROR: {result['error']}")
        if result.get('traceback'):
            print(result['traceback'])


if __name__ == "__main__":
    main()
