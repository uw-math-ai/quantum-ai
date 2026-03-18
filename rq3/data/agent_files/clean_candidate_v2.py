import stim
import re

def main():
    try:
        with open("candidate_graph.stim", "r") as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: candidate_graph.stim not found.")
        return

    # Replace RX with H
    # The graph state output uses RX as initialization to |+>.
    # Since we assume |0> input, H is equivalent.
    content = content.replace("RX", "H")
    
    # Remove TICKs
    content = content.replace("TICK", "")
    
    # Remove empty lines
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    # Reassemble
    final_content = '\n'.join(lines)
    
    # Write to file
    with open("candidate1_clean.stim", "w") as f:
        f.write(final_content)
        
    print("Cleaned circuit saved to candidate1_clean.stim")

if __name__ == "__main__":
    main()
