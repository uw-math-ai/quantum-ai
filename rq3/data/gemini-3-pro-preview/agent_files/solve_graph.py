import stim
import sys

def solve():
    try:
        with open('my_stabilizers.txt', 'r') as f:
            lines = [l.strip() for l in f if l.strip()]
        
        paulis = []
        for l in lines:
            paulis.append(stim.PauliString(l))
            
        t = stim.Tableau.from_stabilizers(paulis, allow_redundant=True, allow_underconstrained=True)
        
        c = t.to_circuit(method="graph_state")
        
        new_c = stim.Circuit()
        for instr in c:
            if instr.name == "RX":
                # RX resets to |+>. Start |0>. H -> |+>.
                new_c.append("H", instr.targets_copy())
            elif instr.name == "RY":
                 # RY resets to |i+>. Start |0>. H -> |+>, S -> |i+>.
                 targets = instr.targets_copy()
                 new_c.append("H", targets)
                 new_c.append("S", targets)
            elif instr.name == "RZ":
                 # RZ resets to |0>. Start |0>. Do nothing.
                 pass
            elif instr.name == "R":
                 # R is Reset Z. Do nothing.
                 pass
            elif instr.name == "TICK":
                 pass
            else:
                new_c.append(instr)
                
        with open('candidate_graph.stim', 'w') as f:
            f.write(str(new_c))
            
        print("Done")
        
    except Exception as e:
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    solve()
