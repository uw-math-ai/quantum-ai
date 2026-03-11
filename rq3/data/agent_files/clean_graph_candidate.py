import re

def clean():
    with open("my_candidate_graph.stim", "r") as f:
        content = f.read()
    
    # Replace RX with H
    # RX is usually at the start.
    # We should be careful not to replace RXY or something if it exists (though Stim doesn't have RXY).
    # But R (reset Z) exists.
    # The output showed "RX 0 1 ...".
    
    # Let's just replace "RX " with "H " globally?
    # Or line by line.
    
    lines = content.splitlines()
    new_lines = []
    for line in lines:
        if line.strip().startswith("RX "):
            new_lines.append(line.replace("RX ", "H "))
        else:
            new_lines.append(line)
            
    new_content = "\n".join(new_lines)
    
    with open("my_candidate_graph_clean.stim", "w") as f:
        f.write(new_content)
        
if __name__ == "__main__":
    clean()
