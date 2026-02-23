import stim

def main():
    circuit_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_49_gemini.stim"
    with open(circuit_path, "r") as f:
        c = stim.Circuit(f.read())
    
    # Print instructions one by one, decomposing if necessary or just printing
    for instruction in c:
        if instruction.name == "CX" and len(instruction.targets_copy()) > 4:
            # Decompose into pairs
            targets = instruction.targets_copy()
            # CX takes pairs.
            # But the stored instruction might be "CX 0 1 0 2 ..."
            # So targets are [0, 1, 0, 2, ...]
            # We can just print chunks
            chunk_size = 6 # 3 pairs
            for i in range(0, len(targets), chunk_size):
                chunk = targets[i:i+chunk_size]
                args = " ".join(str(t.value) for t in chunk)
                print(f"CX {args}")
        elif instruction.name == "H" and len(instruction.targets_copy()) > 10:
             targets = instruction.targets_copy()
             chunk_size = 10
             for i in range(0, len(targets), chunk_size):
                 chunk = targets[i:i+chunk_size]
                 args = " ".join(str(t.value) for t in chunk)
                 print(f"H {args}")
        else:
            print(instruction)

if __name__ == "__main__":
    main()
