import stim

# Load the graph_state based circuit and simplify it
circuit_str = """H 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48
TICK
CZ 0 3 0 5 0 6 1 2 1 5 1 6 2 4 2 25 2 26 2 27 2 39 2 40 2 41 2 46 2 47 2 48 3 4 3 5 3 6 3 25 3 26 3 27 3 39 3 40 3 41 3 46 3 47 3 48 4 5 5 6 6 25 6 26 6 27 6 39 6 40 6 41 6 46 6 47 6 48 7 10 7 12 7 13 8 10 8 11 8 13 9 10 9 11 9 12 10 12 10 13 11 25 11 26 11 27 11 32 11 33 11 34 11 46 11 47 11 48 12 13 12 25 12 26 12 27 12 32 12 33 12 34 12 46 12 47 12 48 13 25 13 26 13 27 13 32 13 33 13 34 13 46 13 47 13 48 14 17 14 19 14 20 15 17 15 18 15 20 16 17 16 18 16 19 17 19 17 20 18 25 18 26 18 27 18 32 18 33 18 34 18 39 18 40 18 41 19 20 19 25 19 26 19 27 19 32 19 33 19 34 19 39 19 40 19 41 20 25 20 26 20 27 20 32 20 33 20 34 20 39 20 40 20 41 21 24 21 26 21 27 22 24 22 25 22 27 23 24 23 25 23 26 28 31 28 33 28 34 29 31 29 32 29 34 30 31 30 32 30 33 35 38 35 40 35 41 36 38 36 39 36 41 37 38 37 39 37 40 42 45 42 47 42 48 43 45 43 46 43 48 44 45 44 46 44 47
TICK
X 1 7 8 10 20 29 30 42
Y 11 12 15
Z 2 3 9 13 14 17 18 25 26 27 32 39 40 41 45 47 48
S 3 5 6 10 12 13 17 19 20
H 0 1 4 7 8 9 14 15 16 24 25 26 27 31 32 33 34 38 39 40 41 45 46 47 48
S 0 7 14"""

circuit = stim.Circuit(circuit_str)

# Count gates
def count_gates(circ):
    stats = {}
    volume = 0
    for instr in circ:
        name = instr.name
        if name == 'TICK':
            continue
        tgt_count = len(instr.targets_copy())
        if name in ['CX', 'CZ']:
            tgt_count = tgt_count // 2  # pairs
        stats[name] = stats.get(name, 0) + tgt_count
        volume += tgt_count
    return stats, volume

stats, vol = count_gates(circuit)
print(f"Stats: {stats}")
print(f"Volume: {vol}")

# Now let's simplify: merge Y into X+S, merge redundant operations, etc.
# Y = i*X*Z, so Y a = X a; S a; Z a; S a (with global phase)
# For state prep, global phase doesn't matter

# Try simplifying by expanding the circuit and then using stim's internal simplification
sim = stim.TableauSimulator()
sim.do(circuit)
tableau = sim.current_inverse_tableau() ** -1

# Get stabilizers
print("\nFinal stabilizers from circuit:")
for i in range(10):  # Just show first 10
    stab = tableau.z_output(i)
    print(f"  Z{i}: {stab}")

# Save the current best circuit
with open('data/claude-opus-4.6/agent_files/best_circuit.stim', 'w') as f:
    f.write(circuit_str)

print(f"\nBest circuit saved. Volume = {vol}")
