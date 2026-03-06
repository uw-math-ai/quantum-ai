def check_file_len():
    with open("stabilizers_84_task.txt", "r") as f:
        for line in f:
            line = line.strip()
            if line:
                print(f"Length: {len(line)}")
                if len(line) != 84:
                    print(f"WRONG LENGTH: {line}")
                    
if __name__ == "__main__":
    check_file_len()
