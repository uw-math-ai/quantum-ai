import stim
import sys

def check_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    # Circuit starts from |0> by default in simulator
    sim.do(circuit)
    
    # Check each stabilizer
    preserved = 0
    for stab in stabilizers:
        # peek_observable_expectation returns +1, -1, or 0 (uncertain)
        exp = sim.peek_observable_expectation(stab)
        if exp == 1:
            preserved += 1
        else:
            # print(f"Failed stabilizer: {stab} (Exp: {exp})")
            pass
            
    return preserved == len(stabilizers)

def main():
    # Read optimized circuit
    with open("data/optimized.stim", "r") as f:
        content = f.read()
    
    # Replace RX with H
    # Note: Stim format allows "RX 0 1 2".
    # We can just replace "RX" with "H" in the text if careful.
    # But "RX" might appear in comments? No.
    # Also "MRX" or "R" or "X" might be substrings?
    # "RX" is a token.
    # Safe replacement: replace "RX " with "H ".
    # And "RX" at end of line?
    
    # Better: parse and modify?
    # Stim circuit modification is hard.
    # Text replacement:
    # "RX" is a gate name.
    # It is usually followed by targets.
    # Let's replace "RX" with "H" if it appears as a word.
    
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        parts = line.split('#')[0].strip().split()
        if not parts:
            new_lines.append(line)
            continue
        
        if parts[0] == "RX":
            # Replace RX with H
            new_line = "H " + " ".join(parts[1:])
            new_lines.append(new_line)
        elif parts[0] == "R":
            # Remove R (Reset Z). Assuming input |0>.
            # If R is used, it resets to |0>. Identity on |0>.
            # So we can drop it.
            pass
        else:
            new_lines.append(line)
            
    final_content = "\n".join(new_lines)
    
    with open("data/final_candidate.stim", "w") as f:
        f.write(final_content)
        
    print("Replaced RX with H and removed R.")
    
    # Load for verification
    circuit = stim.Circuit(final_content)
    
    # Metrics
    cx = 0
    vol = 0
    for instr in circuit:
        if instr.name == "CX":
            n = len(instr.targets_copy()) // 2
            cx += n
            vol += n
        elif instr.name in ["CZ", "CY", "SWAP", "ISWAP"]:
             vol += len(instr.targets_copy()) // 2
        elif instr.name in ["H", "S", "X", "Y", "Z"]:
             vol += len(instr.targets_copy())
             
    print(f"Metrics: CX={cx}, Vol={vol}")
    
    # Verify
    # Load stabilizers
    with open("data/stabilizers_fixed_v2.txt", "r") as f:
        lines = [line.strip().replace(',', '') for line in f.readlines()]
    stabilizers = [stim.PauliString(l) for l in lines if l]
    
    print(f"Verifying {len(stabilizers)} stabilizers...")
    valid = check_stabilizers(circuit, stabilizers)
    if valid:
        print("Verification SUCCESS: All stabilizers preserved.")
    else:
        print("Verification FAILED.")

if __name__ == "__main__":
    main()
