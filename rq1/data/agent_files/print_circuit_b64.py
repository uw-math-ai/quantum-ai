import base64
with open("circuit_28_full.stim", "rb") as f:
    print(base64.b64encode(f.read()).decode('utf-8'))
