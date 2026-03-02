import stim

def find_indices():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_133.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    pattern = "XIIXXIIXXX"
    for i, s in enumerate(stabilizers):
        if pattern in s:
            print(f"[{i}]: {s}")

if __name__ == "__main__":
    find_indices()
