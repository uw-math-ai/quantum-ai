import stim

def check_ghz():
    # GHZ on 8 qubits
    c = stim.Circuit()
    c.append("H", [0])
    for i in range(7):
        c.append("CX", [i, i+1])
    
    # Check stabilizers
    # We want to check if the state is stabilized by XXXXXXXX and ZZZZZZZZ
    # We can use tableau simulation.
    sim = stim.TableauSimulator()
    sim.do_circuit(c)
    
    # Check XXXXXXXX
    # peek_observable_expectation returns +1, -1, or 0
    exp_x = sim.peek_observable_expectation(stim.PauliString("XXXXXXXX"))
    exp_z = sim.peek_observable_expectation(stim.PauliString("ZZZZZZZZ"))
    
    print(f"Expectation XXXXXXXX: {exp_x}")
    print(f"Expectation ZZZZZZZZ: {exp_z}")

if __name__ == "__main__":
    check_ghz()
