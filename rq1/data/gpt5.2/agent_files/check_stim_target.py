import stim
c = stim.Circuit("H 0")
print(dir(c[0].targets_copy()[0]))
