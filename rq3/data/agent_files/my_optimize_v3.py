import stim
import sys

def get_metrics(circuit):
    cx_count = 0
    volume = 0
    for instr in circuit:
        if instr.name in ["CX", "CNOT"]:
            n = len(instr.targets_copy()) // 2
            cx_count += n
            volume += n
        elif instr.name in ["CZ", "CY", "SWAP", "ISWAP", "SQRT_XX", "SQRT_YY", "SQRT_ZZ"]:
            n = len(instr.targets_copy()) // 2
            volume += n
        elif instr.name in ["H", "S", "S_DAG", "X", "Y", "Z", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG"]:
            volume += len(instr.targets_copy())
        elif instr.name in ["RX", "RY", "RZ", "R"]:
            # Resets are 1 volume?
            volume += len(instr.targets_copy())
            
    return cx_count, volume

def main():
    try:
        # Load Baseline
        with open("current_baseline.stim", "r") as f:
            baseline_text = f.read()
        baseline = stim.Circuit(baseline_text)
        base_cx, base_vol = get_metrics(baseline)
        print(f"Baseline: CX={base_cx}, Vol={base_vol}")
        
        # Load Stabilizers
        with open("target_stabilizers_final.txt", "r") as f:
            lines = [line.strip().replace(',', '') for line in f.readlines() if line.strip()]
        
        stabilizers = []
        for line in lines:
            try:
                stabilizers.append(stim.PauliString(line))
            except:
                pass
        
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
        
        # Method 1: Graph State
        try:
            cand_graph = tableau.to_circuit(method="graph_state")
            clean_graph = stim.Circuit()
            
            for instr in cand_graph:
                if instr.name == "RX":
                    clean_graph.append("H", instr.targets_copy())
                elif instr.name == "RY":
                    clean_graph.append("H", instr.targets_copy())
                    clean_graph.append("S", instr.targets_copy())
                elif instr.name == "RZ" or instr.name == "R":
                    pass
                else:
                    clean_graph.append(instr)
            
            c_cx, c_vol = get_metrics(clean_graph)
            print(f"Graph Candidate: CX={c_cx}, Vol={c_vol}")
            
            with open("candidate_graph.stim", "w") as f:
                f.write(str(clean_graph))
        except Exception as e:
            print(f"Graph State Error: {e}")
            
        # Method 2: Elimination
        try:
            cand_elim = tableau.to_circuit(method="elimination")
            e_cx, e_vol = get_metrics(cand_elim)
            print(f"Elim Candidate: CX={e_cx}, Vol={e_vol}")
            
            with open("candidate_elim.stim", "w") as f:
                f.write(str(cand_elim))
        except Exception as e:
            print(f"Elimination Error: {e}")
            
    except Exception as e:
        print(f"Main Error: {e}")

if __name__ == "__main__":
    main()
