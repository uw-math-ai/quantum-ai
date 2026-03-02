import sys
# Create a dummy class to mock the agent tool interface if I were running locally, 
# but here I just want to print the string so I can see it without wrapping?
# No, I can't control the wrapping of the agent's display.
# 
# But wait, I can write a python script that prints the content to a file, and then I can read that file?
# I already have the file!
# 
# I need to invoke `final_circuit(stim_circuit=...)`.
# I cannot invoke it from python.
# 
# I must put the string in the tool call `final_circuit`.
# 
# If I can't copy-paste reliable text, I'm stuck.
# 
# BUT, `check_stabilizers_tool` is not the only way to check.
# I already checked locally with `check_stabilizers_175.py`.
# It passed.
# 
# So I just need to submit.
# 
# I will try to read the file and remove newlines in python, then print it.
# If I print it as one long string, the agent display will wrap it, but the underlying text I copy might be wrapped?
# 
# Actually, the agent tool input `stim_circuit` expects a string.
# I can construct this string in the tool call block.
# 
# If I can't see the string without wrapping, how can I put it in the tool call?
# 
# Maybe I can assume the `circuit_175_candidate.stim` file content is valid.
# I can use `cat` but with a large width? `mode co cols=300`?
# 
# Or I can output it in chunks that are guaranteed to break at spaces.
# 
# Let's try to print it in chunks of 1000 chars, ensuring to break at space.
# 
# But wait, I can't automate the "copy to tool call" step. I have to do it "manually" (as the AI).
# 
# I will try to `type` it again.
# The wrapping `1\n45` suggests the terminal width is small.
# 
# I will write a python script to print the lines one by one, but ensuring lines are not too long.
# I will reformat the circuit to have short lines (e.g. 80 chars).
# Stim allows free formatting.
# So if I reformat `circuit_175_candidate.stim` to have short lines, `type` won't wrap them destructively.
# 
# I'll write `reformat_circuit.py`.

import stim
import sys

# Read original
try:
    with open('data/gemini-3-pro-preview/agent_files/circuit_175_candidate.stim', 'r') as f:
        content = f.read()

    # Naive reformat: replace newlines with spaces, split, then rejoin with max width 80
    tokens = content.replace('\n', ' ').split()
    
    lines = []
    current_line = []
    current_len = 0
    
    for token in tokens:
        if current_len + len(token) + 1 > 80:
            lines.append(" ".join(current_line))
            current_line = [token]
            current_len = len(token)
        else:
            current_line.append(token)
            current_len += len(token) + 1
            
    if current_line:
        lines.append(" ".join(current_line))
        
    with open('data/gemini-3-pro-preview/agent_files/circuit_175_formatted.stim', 'w') as f:
        f.write("\n".join(lines))
        
    print("Formatted circuit saved.")

except Exception as e:
    print(f"Error: {e}")
