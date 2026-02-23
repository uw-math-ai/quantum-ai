import stim
import sys

try:
    with open(r'data\gemini-3-pro-preview\agent_files\circuit_148_fixed.stim', 'r') as f:
        content = f.read()
    circuit = stim.Circuit(content)
    for instruction in circuit:
        # Decompose into individual operations if possible, or just print roughly
        # But actually, let's just use stim's built-in print but ensure it doesn't line-wrap in the library
        # stim doesn't wrap lines by default when converting to string, it puts one instruction per line.
        # But if the instruction is long (many targets), it's one long line.
        # My terminal is wrapping it.
        # So I should break long instructions into multiple smaller instructions.
        
        if instruction.name in ["CX", "H", "R", "M", "X", "Y", "Z"]:
             # These gates can take many targets.
             # We can break them up.
             targets = instruction.targets_copy()
             chunk_size = 4 # small chunk size to avoid wrapping
             for i in range(0, len(targets), chunk_size):
                 chunk = targets[i:i+chunk_size]
                 # Reconstruct a small instruction
                 # Note: we need to handle target types (qubit vs sweep bit etc), but for stabilizer circuits usually just qubits.
                 # Let's just print the name and the targets
                 t_str = " ".join(str(t.value) for t in chunk) # this loses type info (like ! for invert), but for H/CX/etc usually just integers
                 # wait, stim targets have properties.
                 # Better to use stim to format the small instruction
                 
                 # Correct way: create a new circuit with just this small op and print it
                 temp_circ = stim.Circuit()
                 temp_circ.append(instruction.name, chunk)
                 print(str(temp_circ).strip())
        else:
             print(instruction)

except Exception as e:
    print(f"Error: {e}")
