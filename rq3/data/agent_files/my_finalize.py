import stim
import re

def process_circuit(circuit_str):
    lines = circuit_str.splitlines()
    new_lines = []
    for line in lines:
        if line.startswith("RX"):
            # Replace RX with H
            targets = line[3:].strip()
            new_lines.append(f"H {targets}")
        elif line.startswith("TICK"):
            continue
        else:
            new_lines.append(line)
    return "\n".join(new_lines)

def main():
    try:
        with open("best_candidate.stim", "r") as f:
            content = f.read()
        
        final_content = process_circuit(content)
        final_circuit = stim.Circuit(final_content)
        
        # Verify preservation
        with open("current_task_baseline.stim", "r") as f:
            baseline = stim.Circuit(f.read())
            
        sim_base = stim.TableauSimulator()
        sim_base.do(baseline)
        
        sim_final = stim.TableauSimulator()
        sim_final.do(final_circuit)
        
        with open("current_task_stabilizers.txt", "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        targets = [stim.PauliString(l) for l in lines]
        
        base_preserved = 0
        final_preserved = 0
        
        for t in targets:
            if sim_base.peek_observable_expectation(t) == 1:
                base_preserved += 1
            if sim_final.peek_observable_expectation(t) == 1:
                final_preserved += 1
                
        print(f"Baseline preserved: {base_preserved}")
        print(f"Final preserved:    {final_preserved}")
        
        if final_preserved < base_preserved:
            print("ERROR: Final circuit preserves FEWER targets than baseline.")
        else:
            print("SUCCESS: Final circuit preserves at least as many targets.")
            
        # Metrics
        cx = 0
        vol = 0
        for instr in final_circuit:
            n = len(instr.targets_copy())
            if instr.name in ["CX", "CNOT"]:
                cx += n // 2
                vol += n // 2
            elif instr.name in ["CY", "CZ", "SWAP", "ISWAP", "ISWAP_DAG"]:
                vol += n // 2
            elif instr.name in ["H", "S", "S_DAG", "X", "Y", "Z", "I", "SQRT_X", "SQRT_X_DAG", "SQRT_Y", "SQRT_Y_DAG", "SQRT_Z", "SQRT_Z_DAG"]:
                vol += n
        
        print(f"Final Metrics: CX={cx}, Vol={vol}")
        
        with open("final_submission.stim", "w") as f:
            f.write(str(final_circuit))
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
