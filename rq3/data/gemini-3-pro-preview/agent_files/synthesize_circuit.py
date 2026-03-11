
import stim
import os

def solve():
    print("Reading stabilizers...")
    with open("C:/Users/anpaz/Repos/quantum-ai/rq3/data/gemini-3-pro-preview/agent_files/target_stabilizers.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]

    print(f"Read {len(lines)} stabilizers.")
    if not lines:
        print("No stabilizers found.")
        return

    # Check length
    q_len = len(lines[0])
    print(f"Qubits: {q_len}")

    # Create tableau
    try:
        t = stim.Tableau.from_stabilizers([stim.PauliString(l) for l in lines], allow_underconstrained=True)
        print("Tableau created.")
    except Exception as e:
        print(f"Error creating tableau: {e}")
        return

    # Synthesize graph state
    try:
        c = t.to_circuit(method="graph_state")
        print(f"Circuit synthesized. Gates: {len(c)}")
        
        # Save raw
        with open("C:/Users/anpaz/Repos/quantum-ai/rq3/data/gemini-3-pro-preview/agent_files/candidate_raw.stim", "w") as f:
            f.write(str(c))
            
    except Exception as e:
        print(f"Error synthesizing: {e}")

solve()
