import stim
import sys

def analyze():
    try:
        with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers.txt', 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        stabilizers = []
        for i, line in enumerate(lines):
            try:
                stabilizers.append(stim.PauliString(line))
            except Exception as e:
                print(f"Error parsing line {i}: {line}", file=sys.stderr)
                return

        print(f"Loaded {len(stabilizers)} stabilizers.")

        # Check commutativity
        anticommuting_pairs = []
        for i in range(len(stabilizers)):
            for j in range(i + 1, len(stabilizers)):
                if stim.PauliString.commutes(stabilizers[i], stabilizers[j]) == False:
                    anticommuting_pairs.append((i, j))

        if anticommuting_pairs:
            print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
            for i, j in anticommuting_pairs[:5]:
                print(f"  {i} and {j}")
                print(f"  {stabilizers[i]}")
                print(f"  {stabilizers[j]}")
        else:
            print("All stabilizers commute.")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    analyze()
