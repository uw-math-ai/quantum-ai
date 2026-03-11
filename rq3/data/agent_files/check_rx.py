import stim
t = stim.TableauSimulator()
t.do(stim.Circuit("RX 0"))
print(t.peek_observables(["X0", "Z0"]))
