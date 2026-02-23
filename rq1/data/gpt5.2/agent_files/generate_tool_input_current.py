import json

def generate_json():
    stabilizers_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\stabilizers_161_current.txt"
    with open(stabilizers_path, "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]

    circuit_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\circuit_161_fixed.stim"
    with open(circuit_path, "r") as f:
        circuit_str = f.read()

    data = {
        "circuit": circuit_str,
        "stabilizers": stabilizers
    }

    print(json.dumps(data))

if __name__ == "__main__":
    generate_json()
