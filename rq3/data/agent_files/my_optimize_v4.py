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
            volume += len(instr.targets_copy())
            
    return cx_count, volume

def main():
    try:
        # Load Baseline for comparison metrics
        with open("baseline_fresh.stim", "r") as f:
            baseline_text = f.read()
        baseline = stim.Circuit(baseline_text)
        base_cx, base_vol = get_metrics(baseline)
        print(f"Baseline: CX={base_cx}, Vol={base_vol}")
        
        # Load Stabilizers from the file I created
        with open("target_stabilizers_fresh.txt", "r") as f:
            lines = [line.strip().replace(',', '') for line in f.readlines() if line.strip()]
        
        stabilizers = []
        for line in lines:
            try:
                stabilizers.append(stim.PauliString(line))
            except:
                pass
        
        # Create tableau from stabilizers
        # allow_underconstrained=True because we have 34 stabilizers for 36 qubits
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
                elif instr.name == "M" or instr.name == "MX" or instr.name == "MY" or instr.name == "MZ":
                     pass
                else:
                    clean_graph.append(instr)
            
            c_cx, c_vol = get_metrics(clean_graph)
            print(f"Graph Candidate: CX={c_cx}, Vol={c_vol}")
            
            with open("candidate_graph.stim", "w") as f:
                f.write(str(clean_graph))
        except Exception as e:
            print(f"Graph State Error: {e}")
            
    except Exception as e:
        print(f"Main Error: {e}")

if __name__ == "__main__":
    main()
