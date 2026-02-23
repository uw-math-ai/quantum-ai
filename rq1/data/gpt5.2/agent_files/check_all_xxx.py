def check_all_xxx():
    with open("data/gemini-3-pro-preview/agent_files/stabilizers.txt", "r") as f:
        for i, line in enumerate(f):
            if "XXXIIXII" in line:
                print(f"Line {i+1} len {len(line.strip())}: {line.strip()}")

if __name__ == "__main__":
    check_all_xxx()
