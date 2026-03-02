import stim

def analyze():
    filename = "data/gemini-3-pro-preview/agent_files/stabilizers_161_current.txt"
    try:
        with open(filename, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return

    print(f"Number of lines: {len(lines)}")
    if not lines:
        return

    width = len(lines[0])
    print(f"Stabilizer length: {width}")
    
    # Check if all lines have the same length
    for i, line in enumerate(lines):
        if len(line) != width:
            print(f"Error: Line {i} has length {len(line)}, expected {width}")
            return

    all_stabilizers = []
    for line in lines:
        try:
            all_stabilizers.append(stim.PauliString(line))
        except Exception as e:
            print(f"Error parsing line: {line}")
            raise e
            
    # Check commutativity
    anticommuting_pairs = []
    for i in range(len(all_stabilizers)):
        for j in range(i + 1, len(all_stabilizers)):
            if not all_stabilizers[i].commutes(all_stabilizers[j]):
                anticommuting_pairs.append((i, j))
    
    print(f"Number of anticommuting pairs: {len(anticommuting_pairs)}")
    if anticommuting_pairs:
        print("First 10 anticommuting pairs:")
        for pair in anticommuting_pairs[:10]:
            print(f"  {pair}: {lines[pair[0]]} vs {lines[pair[1]]}")

    if len(anticommuting_pairs) == 0:
        try:
            # allow_redundant=True is key because the generators might be linearly dependent
            # allow_underconstrained=True is key because we might not specify 161 generators
            tableau = stim.Tableau.from_stabilizers(all_stabilizers, allow_redundant=True, allow_underconstrained=True)
            print("Stabilizers are commuting and consistent.")
            
            circuit = tableau.to_circuit("elimination")
            print("Circuit generated successfully using stim.Tableau.from_stabilizers")
            
            out_file = "data/gemini-3-pro-preview/agent_files/circuit_161_generated.stim"
            with open(out_file, "w") as f:
                f.write(str(circuit))
            print(f"Circuit saved to {out_file}")
            
        except Exception as e:
            print(f"Error generating circuit: {e}")
    else:
        print("Stabilizers anticommute, cannot generate circuit directly.")

if __name__ == "__main__":
    analyze()
