import sys

def process_file(path):
    with open(path, 'r') as f:
        lines = f.readlines()
        
    stim_lines = []
    ancillas = set()
    
    for line in lines:
        line = line.strip()
        if not line: continue
        if line.startswith("Initial") or line.startswith("Iteration"):
            continue
        stim_lines.append(line)
        
        # Extract ancillas
        parts = line.split()
        # Some lines like "H 0" or "CX 0 1"
        for p in parts:
            if p.isdigit():
                q = int(p)
                if q > 104:
                    ancillas.add(q)
                    
    print("ANCILLAS_START")
    print(",".join(map(str, sorted(list(ancillas)))))
    print("ANCILLAS_END")
    print("CIRCUIT_START")
    print("\n".join(stim_lines))
    print("CIRCUIT_END")

process_file(r"C:\Users\anpaz\Repos\quantum-ai\rq2\data\gemini-3-pro-preview\agent_files_ft\candidate_final.stim")
