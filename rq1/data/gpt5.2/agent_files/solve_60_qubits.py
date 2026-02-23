import stim

def solve():
    with open("data/gemini-3-pro-preview/agent_files/stabilizers_60.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Convert to stim.PauliString
    stabilizers = []
    for line in lines:
        stabilizers.append(stim.PauliString(line))

    # Create tableau
    try:
        # allow_redundant=True in case there are dependent stabilizers
        # allow_underconstrained=True because we only have 60-ish stabilizers for 60 qubits, 
        # but if the number of stabilizers is exactly 60 and they are independent, allow_underconstrained is fine too.
        # Actually, let's count them. 
        # 12 XZZX
        # 12 IXZZX
        # 12 XIXZZ
        # 12 ZXIXZ
        # 5 X...
        # 5 Z...
        # Total = 12*4 + 10 = 58 stabilizers.
        # So it is underconstrained (60 qubits).
        
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_redundant=True, allow_underconstrained=True)
        circuit = tableau.to_circuit("elimination")
        print(circuit)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
