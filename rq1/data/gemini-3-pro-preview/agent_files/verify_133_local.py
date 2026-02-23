import stim
import sys
import os

def clean_and_print():
    # Read the file
    with open("data/gemini-3-pro-preview/agent_files/circuit_133.stim", "r") as f:
        content = f.read()

    # Filter out lines starting with "Success"
    lines = content.splitlines()
    cleaned_lines = [l for l in lines if not l.startswith("Success")]
    
    cleaned_circuit = '\n'.join(cleaned_lines).strip()
    
    # Check if it parses
    try:
        c = stim.Circuit(cleaned_circuit)
        print("Circuit parses successfully.")
        
        # Write to cleaned file
        with open("data/gemini-3-pro-preview/agent_files/circuit_133_cleaned.stim", "w") as f:
            f.write(str(c))
            
    except Exception as e:
        print(f"Failed to parse cleaned circuit: {e}")

if __name__ == "__main__":
    clean_and_print()
