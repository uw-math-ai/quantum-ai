def main():
    with open("data/agent_files/target_stabilizers.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    print(f"Line 26 (len {len(lines[26])}): '{lines[26]}'")
    print(f"Line 71 (len {len(lines[71])}): '{lines[71]}'")

if __name__ == "__main__":
    main()
