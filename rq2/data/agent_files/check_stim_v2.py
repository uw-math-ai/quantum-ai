import stim

print("Checking Stim features")
t = stim.Tableau(2)

# Check prepend_operation
try:
    t.prepend_operation("H", [0])
    print("prepend_operation works")
except Exception as e:
    print(f"prepend_operation failed: {e}")

# Check PauliString indexing
p = stim.PauliString("IXZ")
try:
    val = p[1]
    print(f"PauliString indexing works: {val}")
except Exception as e:
    print(f"PauliString indexing failed: {e}")
