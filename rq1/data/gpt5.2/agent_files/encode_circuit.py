import base64
with open("circuit_135_solution.stim", "rb") as f:
    encoded = base64.b64encode(f.read()).decode('utf-8')
    print(encoded)
