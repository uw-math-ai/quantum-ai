import stim
circuit_text = """
CZ 0 1
2 3
4 5
"""
try:
    c = stim.Circuit(circuit_text)
    print("Parsed successfully")
    print(c)
except Exception as e:
    print(f"Failed: {e}")
