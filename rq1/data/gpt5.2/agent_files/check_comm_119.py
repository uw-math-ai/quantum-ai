import stim
import os

def check_comm():
    filename = r'data\gemini-3-pro-preview\agent_files\stabilizers_119.txt'
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
        
    print(f"Total lines: {len(lines)}")
    # We remove line 95 (index 94 in python? no, index 95 in python 0-indexed)
    # The file has 118 lines (since we skipped blank lines)?
    # Let's see.
    
    # We will only use lines with length 119.
    others = []
    others_indices = []
    for i, line in enumerate(lines):
        if len(line) == 119:
            others.append(stim.PauliString(line))
            others_indices.append(i)
        else:
            print(f"Skipping index {i} with length {len(line)}")
            
    print(f"Checking {len(others)} stabilizers...")
    
    anticommuting = 0
    pairs = []
    for i in range(len(others)):
        for j in range(i+1, len(others)):
            if not others[i].commutes(others[j]):
                anticommuting += 1
                pairs.append((others_indices[i], others_indices[j]))
                
    print(f"Anticommuting pairs among others: {anticommuting}")
    if anticommuting > 0:
        for idx1, idx2 in pairs[:5]:
            print(f"  {idx1} vs {idx2}")
            
    # Now let's try to fix line 95.
    # We found it has 2 extra Is in prefix compared to expected pattern.
    # Expected start: 69. Found: 71.
    # Let's construct a candidate with start 69.
    
    candidate_str = 'I' * 69 + 'ZIIZIIIIIZIIZ' + 'I' * 37
    if len(candidate_str) != 119:
        print(f"Candidate length error: {len(candidate_str)}")
    else:
        try:
            cand = stim.PauliString(candidate_str)
            fails = 0
            for i, p in enumerate(others):
                if not cand.commutes(p):
                    fails += 1
                    # print(f"Candidate anticommutes with index {others_indices[i]}")
            print(f"Fixed candidate (start 69) anticommutes with {fails} others.")
        except Exception as e:
            print(f"Candidate error: {e}")

if __name__ == "__main__":
    check_comm()
