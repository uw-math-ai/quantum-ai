import stim
try:
    c = stim.Circuit("CX 6 6")
    print("CX 6 6 is valid")
except Exception as e:
    print(f"CX 6 6 is invalid: {e}")
