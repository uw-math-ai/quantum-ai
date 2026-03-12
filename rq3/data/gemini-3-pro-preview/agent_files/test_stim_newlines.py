import stim
try:
    c = stim.Circuit("CZ 0 1 \\\n 2 3")
    print("Backslash Valid")
except Exception as e:
    print(f"Backslash Invalid: {e}")

try:
    c = stim.Circuit("CZ 0 1\n 2 3")
    print("Implicit Valid")
except Exception as e:
    print(f"Implicit Invalid: {e}")
