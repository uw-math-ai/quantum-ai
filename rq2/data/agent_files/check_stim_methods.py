
import stim
t = stim.Tableau(2)
try:
    # t.append("H", [0]) # This is wrong based on error
    pass
except TypeError:
    print("append failed")

try:
    # Note: prepend_operation was used in local_validate.py
    # But does it exist in this version?
    # Error message above suggests Tableau expects Tableau for append.
    # What about gate application?
    pass
except AttributeError:
    pass

p = stim.PauliString("IXZ")
try:
    val = p[1]
    print(f"PauliString indexing works: {val}")
except TypeError:
    print("PauliString indexing failed")
except IndexError:
    print("Index error")

try:
    t.prepend_operation("H", [0])
    print("prepend_operation exists")
except AttributeError:
    print("prepend_operation missing")

# Check if we can use circuit
c = stim.Circuit("H 0")
t2 = stim.Tableau.from_circuit(c)
print("from_circuit works")

p = stim.PauliString("IXZ")
try:
    val = p[1]
    print(f"PauliString indexing works: {val}")
except TypeError:
    print("PauliString indexing failed")
except IndexError:
    print("Index error")
