import stim

def debug_simple():
    c = stim.Circuit("H 0")
    sim = stim.TableauSimulator()
    sim.do(c)
    t_inv = sim.current_inverse_tableau()
    p = stim.PauliString("X")
    p_prime = t_inv(p)
    print(f"H 0, Stab X0 -> P': {p_prime}")

if __name__ == "__main__":
    debug_simple()
