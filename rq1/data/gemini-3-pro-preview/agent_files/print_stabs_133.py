import json

def print_stabilizers():
    with open("data/gemini-3-pro-preview/agent_files/stabilizers_133.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    # Print as a single line JSON list
    # But escape newlines to avoid any ambiguity? JSON dumps does that.
    # The issue is the terminal wraps long lines.
    # But if I copy the output, the newlines are usually soft wraps?
    # No, usually they are hard wraps in terminal output capture.
    
    # I will print each stabilizer on a new line, but with a prefix and suffix
    # e.g. STAB: <content> :END
    # And I will split long lines myself if needed, or rely on the fact that I can rejoin them.
    
    for s in stabilizers:
        print(f"STAB:{s}:END")

if __name__ == "__main__":
    print_stabilizers()
