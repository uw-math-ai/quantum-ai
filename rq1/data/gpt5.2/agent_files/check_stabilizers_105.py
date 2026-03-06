#!/usr/bin/env python3
import stim

# Read the stabilizers from file
with open("data/stabilizers_105.txt", "r") as f:
    stabilizers = [l.strip() for l in f if l.strip()]

# Read the circuit
with open("data/gemini-3-pro-preview/agent_files/circuit_105_gemini.stim", "r") as f:
    circuit = f.read()

print("=" * 60)
print(f"STABILIZERS COUNT: {len(stabilizers)}")
if stabilizers:
    print(f"FIRST STABILIZER LENGTH: {len(stabilizers[0])}")
    print(f"FIRST STABILIZER: {stabilizers[0][:50]}...")
    print(f"LAST STABILIZER: {stabilizers[-1][:50] if stabilizers[-1] else 'EMPTY'}")

print("\n" + "=" * 60)
print(f"CIRCUIT LENGTH: {len(circuit)}")

# Verify with stim
print("\n" + "=" * 60)
print("VERIFICATION WITH STIM:")
try:
    sim = stim.TableauSimulator()
    c = stim.Circuit(circuit)
    sim.do(c)
    
    failures = []
    for i, s in enumerate(stabilizers):
        if not s:  # Skip empty lines
            continue
        expectation = sim.peek_observable_expectation(stim.PauliString(s))
        if expectation != 1:
            failures.append((i, s, expectation))
    
    print(f"Total stabilizers: {len(stabilizers)}")
    print(f"Failed stabilizers: {len(failures)}")
    
    if failures:
        print("\nFailed stabilizers details:")
        for idx, stab, exp in failures[:5]:  # Show first 5 failures
            print(f"  [{idx}] Expectation: {exp}")
            print(f"       {stab[:60]}...")
    else:
        print("\n✓ ALL STABILIZERS VERIFIED SUCCESSFULLY!")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
