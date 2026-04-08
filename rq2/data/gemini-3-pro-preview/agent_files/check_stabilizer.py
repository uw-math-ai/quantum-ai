import stim

def get_base_circuit_string():
    return """CX 2 0 0 2 2 0
H 0 4
CX 0 4 0 6 0 7 0 8
H 2 3
CX 2 0 3 0 3 1 1 3 3 1
H 3
CX 1 3 1 6 1 8 1 9 1 10 2 1 2 4 2 5 2 6 2 7 2 8 2 10 2 11 3 2 3 7 3 8 3 9 3 10 5 4 4 5 5 4 4 6 4 8 7 4 9 4 10 4 11 4 7 5 5 7 7 5 5 6 10 5 7 6 6 7 7 6 6 9 6 10 6 11 8 7 7 8 8 7 7 9 8 7 11 7 9 8 8 9 9 8 8 9 10 8 11 8"""

def check_stabilizers():
    base = get_base_circuit_string() # Keep newlines!
    print("Base circuit loaded.")
    sim = stim.TableauSimulator()
    c = stim.Circuit(base)
    sim.do(c)
    print("Simulation done.")
    
    t = sim.current_inverse_tableau().inverse()
    print("Tableau inverted.")
    
    for k in range(12):
        s = t.z_output(k)
        print(f"S{k}: {s}")

if __name__ == "__main__":
    check_stabilizers()

