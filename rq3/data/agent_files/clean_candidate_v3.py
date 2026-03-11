import re

def main():
    try:
        with open("candidate_graph.stim", "r") as f:
            content = f.read()
        
        # Replace RX with H
        # Stim graph state output uses RX at start.
        # RX resets to |+>. H transforms |0> to |+>.
        # Assuming input is |0>, replacing RX with H is valid.
        
        # Replace RX followed by space or newline with H
        content = re.sub(r"\bRX\b", "H", content)
        
        with open("candidate_clean.stim", "w") as f:
            f.write(content)
            
        print("Replaced RX with H in candidate_clean.stim")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
