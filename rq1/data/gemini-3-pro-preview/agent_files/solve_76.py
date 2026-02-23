import stim

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    return [line.strip() for line in lines if line.strip()]

def check_commutativity(stabilizers):
    try:
        paulis = [stim.PauliString(s) for s in stabilizers]
    except Exception as e:
        print(f"Error parsing stabilizers: {e}")
        return []

    n = len(paulis)
    anticommuting_pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            if not paulis[i].commutes(paulis[j]):
                anticommuting_pairs.append((i, j))
    return anticommuting_pairs

def solve(stabilizers):
    try:
        paulis = [stim.PauliString(s) for s in stabilizers]
        # Using allow_underconstrained=True because we might have fewer than N stabilizers
        # Using allow_redundant=True in case some are dependent
        tableau = stim.Tableau.from_stabilizers(paulis, allow_underconstrained=True, allow_redundant=True)
        circuit = tableau.to_circuit("elimination")
        return circuit
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return None

if __name__ == "__main__":
    filename = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers.txt"
    try:
        stabilizers = load_stabilizers(filename)
    except FileNotFoundError:
        print(f"File not found: {filename}")
        exit(1)

    print(f"Loaded {len(stabilizers)} stabilizers.")
    
    anticommuting = check_commutativity(stabilizers)
    if anticommuting:
        print(f"Found {len(anticommuting)} anticommuting pairs.")
        for i, j in anticommuting[:10]:
            print(f"  {i} vs {j}")
            print(f"  Stabilizer {i}: {stabilizers[i]}")
            print(f"  Stabilizer {j}: {stabilizers[j]}")
    else:
        print("All stabilizers commute.")
        
    circuit = solve(stabilizers)
    if circuit:
        print("\nGenerated Circuit:")
        # print(circuit) # Don't print to stdout, it might be huge
        output_file = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_76.stim"
        with open(output_file, "w") as f:
            f.write(str(circuit))
        print(f"Circuit saved to {output_file}")
    else:
        print("Failed to generate circuit.")
