def check_line_42():
    with open("data/gemini-3-pro-preview/agent_files/stabilizers.txt", "r") as f:
        lines = f.readlines()
        if len(lines) >= 42:
            line = lines[41].strip() # 0-indexed
            print(f"Line 42 length: {len(line)}")
            print(f"Line 42 content: {line}")
        else:
            print("File has fewer than 42 lines")

if __name__ == "__main__":
    check_line_42()
