import stim

def load_circuit(filename):
    with open(filename, 'r') as f:
        return stim.Circuit(f.read())

def load_stabilizers(filename):
    with open(filename, 'r') as f:
        stabs = f.read().split(',')
    return [s.strip() for s in stabs]

def check_stabilizers(circuit, stabilizers):
    sim = stim.TableauSimulator()
    sim.do(circuit)
    tableau = sim.current_inverse_tableau()
    tableau = tableau.inverse()
    
    satisfied = []
    unsatisfied = []
    
    # Better way:
    # Use canonicalization or check if stabilizer is +1 eigenstate
    # sim.measure_observable(p) should be deterministic +1
    
    for i, s in enumerate(stabilizers):
        p = stim.PauliString(s)
        obs = sim.peek_observable_expectation(p)
        if obs == 1:
            satisfied.append(s)
        else:
            unsatisfied.append((i, s, obs))
            
    return satisfied, unsatisfied

if __name__ == "__main__":
    circuit = load_circuit("baseline.stim")
    
    # Manually defined stabilizers since file creation might be tedious
    stabs_str = "IIIIXIIIIIXIIIXIXIXIIIIIXIIIIIIIIIIII, IIIIIXIIIIIIXIIXIIIXIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIXIIXXIIIIIIIIIXIIIII, IIIIIIIIIIIIIIIIIIIIIIXIIXIIIIIIIIIXX, IIIXIIIIIIIIIIIIIIIIIIXXIIXIIXIIIIIIX, XIIIIIXIIIIIIIIIIIIIIIIIIIIIIIIIXXIII, IIIIIIIIIXIIIIIXIIIXIIIIIIIIXIIIIIIII, XIIIIIIIIIIIIIIIXIIIIIIIXIXIIXIIXIIII, IXXIIIIIIIIIIIIIIIIIIIIIIIIXIIXIIIIII, IXXIIIIXXIIXIIIIIIIIIIIIIIIIIIIIIIXII, IIIIXIIIXIIIIIXIIIIIIIIIIIIIIIIIIIXII, IIIIIIIIIIXIIIIIIXXIIXIIIIIIIIIIIIIII, XIIXIXXIIIIIXIIIIIIIIIIIIIIIIXIIIIIII, IIXIIIIIIIIXIXIIIIIIIIIIIIIIIIXIIIIII, IIIIIIIXIIIXIXIIIIIIIIXXIXIIIIIIIIIII, IIIIIIIXXIIIIIXIXIIIIIIXIIXIIIIIIIIII, IIIIIIIIIIIIIIIIIIXIIXIIXIIIIIIXXXIII, IIIXIXIIIXIIIIIXIIIIIIIIIIIIIIIIIIIXX, IIIIZIIIIIZIIIZIZIZIIIIIZIIIIIIIIIIII, IIIIIZIIIIIIZIIZIIIZIIIIIIIIIIIIIIIII, IIIIIIIIIIIIIIIIIZIIZZIIIIIIIIIZIIIII, IIIIIIIIIIIIIIIIIIIIIIZIIZIIIIIIIIIZZ, IIIZIIIIIIIIIIIIIIIIIIZZIIZIIZIIIIIIZ, ZIIIIIZIIIIIIIIIIIIIIIIIIIIIIIIIZZIII, IIIIIIIIIZIIIIIZIIIZIIIIIIIIZIIIIIIII, ZIIIIIIIIIIIIIIIZIIIIIIIZIZIIZIIZIIII, IZZIIIIIIIIIIIIIIIIIIIIIIIIZIIZIIIIII, IZZIIIIZZIIZIIIIIIIIIIIIIIIIIIIIIIZII, IIIIZIIIZIIIIIZIIIIIIIIIIIIIIIIIIIZII, IIIIIIIIIIZIIIIIIZZIIZIIIIIIIIIIIIIII, ZIIZIZZIIIIIZIIIIIIIIIIIIIIIIZIIIIIII, IIZIIIIIIIIZIZIIIIIIIIIIIIIIIIZIIIIII, IIIIIIIZIIIZIZIIIIIIIIZZIZIIIIIIIIIII, IIIIIIIZZIIIIIZIZIIIIIIZIIZIIIIIIIIII, IIIIIIIIIIIIIIIIIIZIIZIIZIIIIIIZZZIII, IIIZIZIIIZIIIIIZIIIIIIIIIIIIIIIIIIIZZ"
    stabilizers = [s.strip() for s in stabs_str.split(',')]
    
    satisfied, unsatisfied = check_stabilizers(circuit, stabilizers)
    print(f"Satisfied: {len(satisfied)}")
    print(f"Unsatisfied: {len(unsatisfied)}")
    for i, s, obs in unsatisfied:
        print(f"Stabilizer {i}: {s} -> {obs}")
        
    # Also print circuit instructions with index
    print("\nCircuit instructions:")
    for i, instr in enumerate(circuit.flattened()):
        print(f"{i}: {instr}")
