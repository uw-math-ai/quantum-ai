import stim
circuit_text = """
CX 0 
1
"""
try:
    c = stim.Circuit(circuit_text)
    print("Success")
except Exception as e:
    print(f"Error: {e}")
