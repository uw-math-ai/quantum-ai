import stim

try:
    s = stim.TableauSimulator()
    p = stim.PauliString("X")
    print(s.peek_observable_expectation(p))
except AttributeError:
    print("No peek_observable_expectation")
except Exception as e:
    print(e)
