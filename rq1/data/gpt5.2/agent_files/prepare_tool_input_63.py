import json

def generate_tool_call():
    try:
        with open("stabilizers_63_qubits.txt", "r") as f:
            stabilizers = [line.strip() for line in f if line.strip()]
        
        with open("circuit_63_new.stim", "r") as f:
            circuit = f.read()

        tool_call = {
            "circuit": circuit,
            "stabilizers": stabilizers
        }
        
        with open("tool_input_63.json", "w") as f:
            json.dump(tool_call, f)
            
        print("Generated tool input in tool_input_63.json")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_tool_call()
