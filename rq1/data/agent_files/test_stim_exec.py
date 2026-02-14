import stim
try:
    c = stim.Circuit('CX 0 1 0 2')
    sim = stim.TableauSimulator()
    sim.do(c)
    print("Execution successful")
except Exception as e:
    print(f"Execution failed: {e}")
