import stim
import numpy as np

def get_baseline():
    return """H 0 1 3
CX 0 1 0 3 0 6 0 8 6 1 1 6 6 1 1 5
H 2
CX 2 5 3 4 6 4 4 6 6 4 4 5 4 6 4 8 7 6 8 6 8 7"""

def analyze():
    # Manual list of instructions
    ops = [
        "H 0 1 3",
        "CX 0 1", "CX 0 3", "CX 0 6", "CX 0 8",
        "CX 6 1", "CX 1 6", "CX 6 1", # SWAP 1 6
        "CX 1 5",
        "H 2",
        "CX 2 5",
        "CX 3 4",
        "CX 6 4",
        "CX 4 6", "CX 6 4", # SWAP 4 6
        "CX 4 5",
        "CX 4 6", # Wait. Original: 6 4 4 6 6 4 4 5 4 6 4 8...
        # 6 4, 4 6, 6 4 (SWAP)
        # 4 5
        # 4 6
        # 4 8
        "CX 4 8",
        "CX 7 6",
        "CX 8 6",
        "CX 8 7"
    ]
    
    stabilizers_str = [
        "XXIXXIIII", # 0
        "IIIIXXIXX", # 1
        "IIXIIXIII", # 2
        "IIIXIIXII", # 3
        "IIIZZIZZI", # 4
        "IZZIZZIII", # 5
        "ZZIIIIIII", # 6
        "IIIIIIIZZ"  # 7
    ]
    
    sim = stim.TableauSimulator()
    step = 0
    
    print("Step 0 (Start):")
    
    for op in ops:
        circuit_chunk = stim.Circuit(op)
        sim.do(circuit_chunk)
        step += 1
        
        valid_indices = []
        for i, s in enumerate(stabilizers_str):
            try:
                p = stim.PauliString(s)
                val = sim.peek_observable_expectation(p)
                if abs(val) > 0.99:
                    valid_indices.append(i)
            except:
                pass
        print(f"Step {step} ({op}): Valid: {valid_indices}")


if __name__ == "__main__":
    analyze()
