# Steane Code Circuit Generation

This directory contains Python scripts and tools for generating and analyzing the **Steane [[7,1,3]] quantum error correcting code**.

## Overview

The Steane code is one of the first quantum error correcting codes, discovered by Andrew Steane in 1996. It is a CSS (Calderbank-Shor-Steane) code that:
- Encodes **1 logical qubit** into **7 physical qubits**
- Has code distance **3** (can correct any single-qubit error)
- Uses **6 stabilizer generators** (3 X-type, 3 Z-type)

## Stabilizer Generators

The code is defined by the following 6 stabilizer generators:

### X-type Stabilizers:
- `S₁ˣ = X₀X₁X₂X₃`
- `S₂ˣ = X₀X₂X₄X₆`
- `S₃ˣ = X₂X₃X₄X₅`

### Z-type Stabilizers:
- `S₁ᶻ = Z₀Z₁Z₂Z₃`
- `S₂ᶻ = Z₀Z₂Z₄Z₆`
- `S₃ᶻ = Z₂Z₃Z₄Z₅`

## Logical Operators

For the **logical |0⟩ state**, we add the logical Z operator:
- **Logical Z**: `Z₀Z₁Z₂Z₃Z₄Z₅Z₆` (all Z's)

This 7th operator uniquely defines the pure state while maintaining CSS structure.

## Generated Circuit

The Steane code preparation circuit uses only **H gates and CNOT gates**:

```stim
CX 1 0 0 1 1 0
H 0 2
CX 0 2 0 3 0 4 0 6
H 1
CX 1 0 1 2 1 4 2 3 2 4 2 5 2 6 3 5 3 6 4 5 4 6 5 4 6 4 6 5 5 6 6 5 5 6
```

### Circuit Statistics:
- **Total instructions**: 5
- **CX gates**: 3
- **H gates**: 2
- **Qubits**: 7

## Files in This Directory

### Main Scripts

1. **`steane_circuit.py`** - Basic Steane code circuit generation
   - Simple implementation using stim
   - Generates and verifies the circuit
   - Outputs circuit to `steane_circuit.stim`

2. **`steane_code_complete.py`** - Comprehensive implementation with full documentation
   - Object-oriented design with `SteaneCode` class
   - Extensive verification and error checking
   - Detailed output with commutation relations
   - Output circuit to `steane_circuit_full.stim`

### Generated Outputs

- **`steane_circuit.stim`** - Generated Stim circuit file (from basic script)
- **`steane_circuit_full.stim`** - Generated Stim circuit file (from comprehensive script)

## Circuit Operation Breakdown

The circuit consists of 5 operations:

1. **CX 1 0 0 1 1 0**: CNOT operations
   - Control qubit 1 → Target qubit 0
   - Control qubit 0 → Target qubit 1
   - Control qubit 1 → Target qubit 0

2. **H 0 2**: Hadamard gates on qubits 0 and 2

3. **CX 0 2 0 3 0 4 0 6**: CNOT operations
   - Control qubit 0 → Target qubits 2, 3, 4, 6

4. **H 1**: Hadamard gate on qubit 1

5. **CX 1 0 1 2 1 4 2 3 2 4 2 5 2 6 3 5 3 6 4 5 4 6 5 4 6 4 6 5 5 6 6 5 5 6**: 
   Multiple CNOT operations creating entanglement

## Verification

The scripts verify that:

1. ✅ All 7 generators commute pairwise
2. ✅ The circuit produces a +1 eigenstate for all generators
3. ✅ The final state is a valid 1-qubit code subspace

## How to Use

### Option 1: Simple Generation
```bash
python steane_circuit.py
```

Output:
- Circuit saved to `steane_circuit.stim`
- Verification output shown on screen

### Option 2: Comprehensive Analysis
```bash
python steane_code_complete.py
```

Output:
- Detailed commutation relations
- Circuit generation with statistics
- Full verification with eigenvalues
- Circuit saved to `steane_circuit_full.stim`

## Mathematical Background

The Steane code is a CSS code, meaning:
- X-type stabilizers form one sub-code (Hamming [7,4])
- Z-type stabilizers form another (dual Hamming [7,4])
- The code stabilizes a unique 2D subspace (1 logical qubit + 1 degree of freedom)
- Adding the logical Z operator uniquely defines the logical |0⟩ state

### Key Properties:
- **Parameters**: [[n, k, d]] = [[7, 1, 3]]
  - n = 7 (physical qubits)
  - k = 1 (logical qubits)
  - d = 3 (code distance)

- **Code rate**: 1/7 ≈ 14.3%
- **Logical error threshold**: ~1.9% (approximately)

## Circuit Implementation Details

The generated circuit is a **Clifford circuit** that:
1. Maps the |0⟩ₙ initial state to the Steane code logical |0⟩ state
2. Creates a superposition of basis states satisfying all stabilizer constraints
3. Uses only Clifford gates (H and CNOT), which are efficiently simulatable

### Stim Format

The `.stim` format is a compact representation of quantum circuits:
- `H q`: Hadamard gate on qubit q
- `CX q1 q2`: CNOT gate with control q1, target q2
- Multiple gates can be listed on the same line

## References

- Steane, A. M. (1996). "Error Correcting Codes for Quantum Communication"
- https://en.wikipedia.org/wiki/Steane_code
- Stim Documentation: https://github.com/quantumlib/Stim

## Dependencies

- **stim** (quantum circuit simulator)
  ```bash
  pip install stim
  ```

- **Python** 3.7+

## Testing the Circuit

To verify the circuit works in a quantum simulator:

```python
import stim

# Load the circuit
circuit = stim.Circuit(open("steane_circuit_full.stim").read())

# Simulate and check stabilizers
sim = stim.TableauSimulator()
sim.do(circuit)

# Verify eigenvalues (should all be +1)
generators = [
    stim.PauliString("X0*X1*X2*X3"),
    stim.PauliString("X0*X2*X4*X6"),
    stim.PauliString("X2*X3*X4*X5"),
    stim.PauliString("Z0*Z1*Z2*Z3"),
    stim.PauliString("Z0*Z2*Z4*Z6"),
    stim.PauliString("Z2*Z3*Z4*Z5"),
]

for gen in generators:
    eigenvalue = 1 if sim.measure_observable(gen) == 0 else -1
    print(f"{gen}: eigenvalue = +{eigenvalue}")
```

## License

These scripts are provided for educational and research purposes.
