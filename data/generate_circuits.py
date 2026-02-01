import stim
import random
import json
from typing import List, Dict, Any

def permute_stabilizers(generators: List[str], num_qubits: int) -> tuple[List[str], List[int]]:
    """
    Randomly relabels qubit indices in the stabilizer strings.
    """
    indices = list(range(num_qubits))
    random.shuffle(indices)
    mapping = {old: new for old, new in enumerate(indices)}
    
    new_generators = []
    for stab in generators:
        new_chars = ['I'] * num_qubits
        for i, char in enumerate(stab):
            if char != 'I':
                new_pos = mapping[i]
                new_chars[new_pos] = char
        new_generators.append("".join(new_chars))
        
    return new_generators, indices

def generate_naive_circuit(stabilizers: List[str]) -> str:
    """
    Uses Stim's Gaussian elimination to generate a baseline state-prep circuit.
    """
    stim_stabs = [stim.PauliString(s) for s in stabilizers]
    try:
        tableau = stim.Tableau.from_stabilizers(
            stim_stabs, 
            allow_redundant=False, 
            allow_underconstrained=True
        )
        circuit = tableau.to_circuit(method="elimination")
        return str(circuit)
    except Exception as e:
        return ""

def process_code_entry_identity_only(code_def: Dict[str, Any]) -> Dict:
    """
    Generates a single circuit for the identity permutation only (no variations).
    """
    n = code_def["physical_qubits"]
    identity_perm = list(range(n))
    
    entry = {
        "source_code": code_def["name"],
        "d": code_def.get("d"),
        "permutation": identity_perm,
        "input_stabilizers": code_def["generators"],
        "output_circuit": generate_naive_circuit(code_def["generators"]).replace("\n", "\\n")
    }
    
    return entry

def process_code_entry(code_def: Dict[str, Any], num_variations: int = 50) -> List[Dict]:
    import math
    dataset = []
    
    # physical_qubits count
    n = code_def["physical_qubits"]
    
    # Calculate maximum possible unique permutations
    max_permutations = math.factorial(n)
    if num_variations > max_permutations:
        print(f"  WARNING: Requested {num_variations} variations but only {max_permutations} unique permutations exist for {n} qubits")
        num_variations = max_permutations

    # Track used permutations (as tuples for hashability)
    used_permutations = set()

    # --- STEP 1: Add the Original (Identity Permutation) ---
    identity_perm = list(range(n))
    used_permutations.add(tuple(identity_perm))
    
    original_entry = {
        "source_code": code_def["name"],
        "d": code_def.get("d"),
        "permutation": identity_perm,
        "input_stabilizers": code_def["generators"],
        "output_circuit": generate_naive_circuit(code_def["generators"]).replace("\n", "\\n")
    }
    dataset.append(original_entry)

    # --- STEP 2: Add Random Variations (ensuring uniqueness) ---
    attempts = 0
    max_attempts = num_variations * 100  # Prevent infinite loops
    
    while len(dataset) < num_variations and attempts < max_attempts:
        attempts += 1
        
        new_stabs, perm = permute_stabilizers(
            code_def["generators"], 
            n
        )
        
        # Check if this permutation is unique
        perm_tuple = tuple(perm)
        if perm_tuple in used_permutations:
            continue  # Skip duplicate
        
        circuit_str = generate_naive_circuit(new_stabs)
        
        if circuit_str:
            used_permutations.add(perm_tuple)
            entry = {
                "source_code": code_def["name"],
                "d": code_def.get("d"),
                "permutation": perm,
                "input_stabilizers": new_stabs,
                "output_circuit": circuit_str.replace("\n", "\\n")
            }
            dataset.append(entry)
    
    if len(dataset) < num_variations:
        print(f"  WARNING: Only generated {len(dataset)} unique variations (requested {num_variations})")
            
    return dataset

def save_to_jsonl(data: List[Dict], filename: str):
    """
    Saves the list of dictionaries to a JSONL file.
    """
    with open(filename, 'w') as f:
        for entry in data:
            f.write(json.dumps(entry) + '\n')

if __name__ == "__main__":
    import os
    import argparse
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Generate quantum circuit dataset from benchmarks')
    parser.add_argument('-n', '--num-variations', type=int, default=50,
                        help='Number of variations per code (default: 50)')
    parser.add_argument('-o', '--output', type=str, default='data/circuit_dataset.jsonl',
                        help='Output filename (default: data/circuit_dataset.jsonl)')
    parser.add_argument('-l', '--limit', type=int, default=None,
                        help='Limit number of codes to process (default: all)')
    parser.add_argument('--identity-only', action='store_true',
                        help='Generate only identity permutation circuits (no variations)')
    parser.add_argument('--verbose', action='store_true',
                        help='Print detailed progress information')
    
    args = parser.parse_args()
    
    # Read benchmarks.json
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'benchmarks.json')
    
    print(f"Reading benchmarks from: {json_path}")
    with open(json_path, 'r') as f:
        benchmarks = json.load(f)
    
    print(f"Found {len(benchmarks)} codes in benchmarks.json")
    
    # Limit codes if requested
    if args.limit:
        benchmarks = benchmarks[:args.limit]
        print(f"Processing first {args.limit} codes only")
    
    # Generate dataset
    all_training_data = []
    
    if args.identity_only:
        print("\n=== Identity-only mode (no permutations) ===\n")
        for i, code_info in enumerate(benchmarks, 1):
            print(f"[{i}/{len(benchmarks)}] Processing: {code_info['name']}")
            
            try:
                entry = process_code_entry_identity_only(code_info)
                all_training_data.append(entry)
                
                if args.verbose:
                    print(f"  Circuit length: {len(entry['output_circuit'])} chars")
                    
            except Exception as e:
                print(f"  ERROR: Failed to process {code_info['name']}: {str(e)}")
                continue
    else:
        print(f"\n=== Generating {args.num_variations} variations per code ===\n")
        for i, code_info in enumerate(benchmarks, 1):
            print(f"\n[{i}/{len(benchmarks)}] Processing: {code_info['name']}")
            print(f"  Physical qubits: {code_info['physical_qubits']}, "
                  f"Logical qubits: {code_info['logical_qubits']}, "
                  f"Distance: {code_info['d']}")
            
            try:
                code_data = process_code_entry(code_info, num_variations=args.num_variations)
                all_training_data.extend(code_data)
                print(f"  Generated {len(code_data)} variations")
                
                if args.verbose and code_data:
                    print(f"  Sample circuit length: {len(code_data[0]['output_circuit'])} chars")
                    
            except Exception as e:
                print(f"  ERROR: Failed to process {code_info['name']}: {str(e)}")
                continue
    
    # Save to file
    print(f"\n{'='*60}")
    print(f"Total examples generated: {len(all_training_data)}")
    print(f"Saving to: {args.output}")
    
    save_to_jsonl(all_training_data, args.output)
    
    print(f"\nDataset saved successfully!")
    print(f"Total size: {len(all_training_data)} examples")
    print(f"Codes processed: {len(benchmarks)}")
    if not args.identity_only:
        print(f"Average examples per code: {len(all_training_data) / len(benchmarks):.1f}")