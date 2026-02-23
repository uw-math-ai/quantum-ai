import stim
import sys

def solve():
    input_file = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_81.txt"
    output_file = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_81_new.stim"

    try:
        with open(input_file, "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        stabilizers = []
        for i, line in enumerate(lines):
            if len(line) != 81:
                print(f"Warning: Line {i+1} has length {len(line)}: '{line}'")
            stabilizers.append(stim.PauliString(line))

        print(f"Loaded {len(stabilizers)} stabilizers.")

        # Check commutativity
        anticommuting_pairs = []
        for i in range(len(stabilizers)):
            for j in range(i + 1, len(stabilizers)):
                if not stabilizers[i].commutes(stabilizers[j]):
                    anticommuting_pairs.append((i, j))

        if anticommuting_pairs:
            print(f"Found {len(anticommuting_pairs)} anticommuting pairs!")
            for i, j in anticommuting_pairs[:5]:
                print(f"  {i} and {j}")
            # If they don't commute, we can't form a stabilizer state satisfying all of them.
            # But let's see what happens.
        else:
            print("All stabilizers commute.")

        # Create a tableau
        tableau = stim.Tableau.from_stabilizers(
            stabilizers,
            allow_underconstrained=True,
            allow_redundant=True
        )

        print(f"Tableau created. Num qubits: {len(tableau)}")

        circuit = tableau.to_circuit("elimination")
        
        with open(output_file, "w") as f:
            f.write(str(circuit))
            
        print(f"Circuit generated successfully and written to {output_file}.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    solve()
