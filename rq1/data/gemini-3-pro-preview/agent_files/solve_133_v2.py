import stim

def solve():
    with open("data/gemini-3-pro-preview/agent_files/stabilizers_133.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    print(f"Read {len(stabilizers)} stabilizers.")

    t = stim.Tableau.from_stabilizers(
        [stim.PauliString(s) for s in stabilizers],
        allow_underconstrained=True
    )
    
    c = t.to_circuit()
    with open("data/gemini-3-pro-preview/agent_files/circuit_133_v2.stim", "w") as f:
        f.write(str(c))
        
if __name__ == "__main__":
    solve()
