def main():
    with open("data/agent_files/target_stabilizers.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    lengths = [len(line) for line in lines]
    print(f"Min length: {min(lengths)}")
    print(f"Max length: {max(lengths)}")
    if min(lengths) != max(lengths):
        print("Lengths are inconsistent!")
        for i, l in enumerate(lengths):
            if l != 105:
                print(f"Line {i} has length {l}")

if __name__ == "__main__":
    main()
