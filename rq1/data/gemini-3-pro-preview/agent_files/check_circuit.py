import stim

def fix_circuit():
    with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_76.stim", "r") as f:
        circuit_text = f.read()
    
    # Parse the circuit using stim to ensure it's valid
    try:
        circuit = stim.Circuit(circuit_text)
        print("Circuit is valid.")
        return circuit
    except Exception as e:
        print(f"Circuit is invalid: {e}")
        return None

if __name__ == "__main__":
    circuit = fix_circuit()
