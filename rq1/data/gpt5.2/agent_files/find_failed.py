def find_line():
    target = "XXXIIXII"
    with open("data/gemini-3-pro-preview/agent_files/stabilizers.txt", "r") as f:
        for i, line in enumerate(f):
            if target in line:
                print(f"Line {i+1}: {line.strip()}")


if __name__ == "__main__":
    find_line()
