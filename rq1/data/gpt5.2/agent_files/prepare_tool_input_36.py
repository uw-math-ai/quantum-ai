import json

def prepare():
    with open("circuit_36_anpaz.stim", "r") as f:
        circuit = f.read().strip()
    
    with open("stabilizers_36_anpaz.txt", "r") as f:
        stabs = [l.strip() for l in f if l.strip()]

    output = {
        "circuit": circuit,
        "stabilizers": stabs
    }
    print(json.dumps(output))

if __name__ == "__main__":
    prepare()
