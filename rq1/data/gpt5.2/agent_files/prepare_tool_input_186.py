import json
import stim

def prepare():
    # Read circuit
    with open("circuit_186_final.stim", "r") as f:
        circuit = f.read()
    
    # Read original stabilizers and fix line 105
    with open("stabilizers_186.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    if len(lines[105]) == 184:
        lines[105] = "II" + lines[105]

    # Verify length 186
    for line in lines:
        if len(line) != 186:
            print(f"Error: {len(line)}")
            return

    output = {
        "circuit": circuit,
        "stabilizers": lines
    }
    
    with open("tool_input_186.json", "w") as f:
        json.dump(output, f)

if __name__ == "__main__":
    prepare()
