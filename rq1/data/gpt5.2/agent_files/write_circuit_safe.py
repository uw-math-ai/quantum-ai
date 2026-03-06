import stim

def main():
    circuit_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_49_gemini.stim"
    output_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\final_safe.stim"
    
    with open(circuit_path, "r") as f:
        c = stim.Circuit(f.read())
    
    with open(output_path, "w") as out:
        for instruction in c:
            if instruction.name == "CX" and len(instruction.targets_copy()) > 4:
                targets = instruction.targets_copy()
                chunk_size = 6
                for i in range(0, len(targets), chunk_size):
                    chunk = targets[i:i+chunk_size]
                    args = " ".join(str(t.value) for t in chunk)
                    out.write(f"CX {args}\n")
            elif instruction.name == "H" and len(instruction.targets_copy()) > 10:
                 targets = instruction.targets_copy()
                 chunk_size = 10
                 for i in range(0, len(targets), chunk_size):
                     chunk = targets[i:i+chunk_size]
                     args = " ".join(str(t.value) for t in chunk)
                     out.write(f"H {args}\n")
            else:
                out.write(str(instruction) + "\n")

    print(f"Wrote safe circuit to {output_path}")

if __name__ == "__main__":
    main()
