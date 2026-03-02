import stim
import sys

def verify():
    # Load stabilizers
    with open(r'data/gemini-3-pro-preview/agent_files/stabilizers_186_clean.txt', 'r') as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    s = stabilizers[0]
    print(f"Stabilizer 0 length: {len(s)}")
    print(f"Stabilizer 0 content: {repr(s)}")

if __name__ == "__main__":
    verify()
