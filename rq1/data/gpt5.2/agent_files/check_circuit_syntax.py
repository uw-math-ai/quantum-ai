import stim
try:
    with open("circuit_35_generated.stim", "r") as f:
        content = f.read()
    circuit = stim.Circuit(content)
    print("Circuit parsed successfully.")
except Exception as e:
    print(f"Circuit parsing failed: {e}")
