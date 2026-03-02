import stim

def solve():
    with open(r'data/gemini-3-pro-preview/agent_files/stabilizers_186.txt') as f:
        lines = [line.strip() for line in f if line.strip()]

    stabilizers = [stim.PauliString(line) for line in lines]
    
    try:
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
        circuit = tableau.to_circuit()
        with open(r'data/gemini-3-pro-preview/agent_files/circuit_186.stim', 'w') as f:
            f.write(str(circuit))
        print("Success! Circuit written to circuit_186.stim")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
