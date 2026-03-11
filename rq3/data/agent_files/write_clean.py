
content = """import stim

def clean():
    try:
        with open('candidate_raw.stim', 'r') as f:
            lines = f.readlines()
        
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Replace RX with H
            if line.startswith("RX "):
                cleaned_lines.append(line.replace("RX ", "H "))
            elif line.startswith("TICK"):
                continue
            else:
                cleaned_lines.append(line)
        
        # Parse and save
        circuit = stim.Circuit("\\n".join(cleaned_lines))
        with open('candidate_final.stim', 'w') as f:
            f.write(str(circuit))
        print("Cleaned circuit saved to candidate_final.stim")
        print(f"CX count: {sum(1 for op in circuit if op.name == 'CX')}")
        print(f"CZ count: {sum(1 for op in circuit if op.name == 'CZ')}")
        
    except Exception as e:
        print(f"Error cleaning: {e}")

if __name__ == "__main__":
    clean()
"""

with open("clean_candidate.py", "w") as f:
    f.write(content)
