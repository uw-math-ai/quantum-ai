import stim

c = stim.Circuit("RX 0")
print(f"Instruction: {c[0]}")
print(f"Is reset? {c[0].name == 'RX'}") 
# In stim, 'RX' is indeed a Reset into X basis. 
# 'R' is Reset into Z basis (0).
# 'RY' is Reset into Y basis.
