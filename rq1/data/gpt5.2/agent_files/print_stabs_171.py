import json
def print_stabs():
    with open("stabilizers_171.txt", "r") as f:
        stabs = [line.strip() for line in f if line.strip()]
    print(json.dumps(stabs))

if __name__ == "__main__":
    print_stabs()
