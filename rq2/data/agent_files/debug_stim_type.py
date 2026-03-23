import stim
c = stim.Circuit("H 0")
ops = list(c.flattened_operations())
print(f"Type of ops[0]: {type(ops[0])}")
print(f"Dir: {dir(ops[0])}")
try:
    print(ops[0].targets_copy())
except AttributeError as e:
    print(e)
