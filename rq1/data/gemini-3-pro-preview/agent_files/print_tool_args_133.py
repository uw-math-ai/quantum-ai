import json

def print_args():
    with open("data/gemini-3-pro-preview/agent_files/stabilizers_133.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    with open("data/gemini-3-pro-preview/agent_files/circuit_133_cleaned.stim", "r") as f:
        circuit = f.read().strip()

    print("CIRCUIT_START")
    print(circuit)
    print("CIRCUIT_END")
    print("STABILIZERS_START")
    print(json.dumps(stabilizers))
    print("STABILIZERS_END")

if __name__ == "__main__":
    print_args()
