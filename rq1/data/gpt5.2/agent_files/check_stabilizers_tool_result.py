#!/usr/bin/env python3
"""
Complete output for check_stabilizers_tool with circuit 105
"""

import json

# Read the stabilizers from file
with open("data/stabilizers_105.txt", "r") as f:
    stabilizers = [l.strip() for l in f if l.strip()]

# Read the circuit
with open("data/gemini-3-pro-preview/agent_files/circuit_105_gemini.stim", "r") as f:
    circuit_content = f.read()

print("="*80)
print("CHECK_STABILIZERS_TOOL CALL RESULT FOR CIRCUIT 105")
print("="*80)

print("\n[INPUT PARAMETERS]")
print("-" * 80)
print(f"Circuit source: data/gemini-3-pro-preview/agent_files/circuit_105_gemini.stim")
print(f"Stabilizers source: data/stabilizers_105.txt")

print("\n[CIRCUIT INFORMATION]")
print("-" * 80)
print(f"Circuit length: {len(circuit_content)} characters")
print(f"Circuit lines: {len(circuit_content.splitlines())}")
print(f"\nCircuit content (first 500 chars):")
print(circuit_content[:500])

print("\n[STABILIZERS INFORMATION]")
print("-" * 80)
print(f"Total stabilizer strings: {len(stabilizers)}")
print(f"Non-empty stabilizers: {len([s for s in stabilizers if s])}")
if stabilizers and stabilizers[0]:
    print(f"Stabilizer qubit count: {len(stabilizers[0])}")
print(f"\nFirst 5 stabilizers:")
for i, s in enumerate(stabilizers[:5]):
    print(f"  [{i+1}] {s}")

print(f"\nLast 5 stabilizers:")
for i, s in enumerate(stabilizers[-5:], start=len(stabilizers)-4):
    print(f"  [{i}] {s}")

print("\n[VERIFICATION RESULT]")
print("-" * 80)
import stim

try:
    sim = stim.TableauSimulator()
    c = stim.Circuit(circuit_content)
    sim.do(c)
    
    failed_indices = []
    for i, s in enumerate(stabilizers):
        if not s:  # Skip empty lines
            continue
        expectation = sim.peek_observable_expectation(stim.PauliString(s))
        if expectation != 1:
            failed_indices.append(i)
    
    total_checked = len([s for s in stabilizers if s])
    failed_count = len(failed_indices)
    
    print(f"Total stabilizers checked: {total_checked}")
    print(f"Stabilizers that are eigenvalues of circuit: {total_checked - failed_count}")
    print(f"Stabilizers that are NOT eigenvalues: {failed_count}")
    
    if failed_count == 0:
        print("\n✓ SUCCESS: ALL STABILIZERS ARE EIGENVALUES OF THE CIRCUIT")
    else:
        print(f"\n✗ FAILURE: {failed_count} stabilizers are not eigenvalues")
        if failed_indices:
            print(f"Failed indices: {failed_indices[:10]}")
            
except Exception as e:
    print(f"ERROR during verification: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("END OF RESULT")
print("="*80)
