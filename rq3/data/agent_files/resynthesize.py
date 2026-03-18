import stim

baseline_text = """
CX 1 0 0 1 1 0
H 0 1 2 3 6 9
CX 0 1 0 2 0 3 0 6 0 9 0 12 0 14 0 15 0 16 0 20 0 21 0 22
H 4 5 10
CX 3 0 4 0 5 0 9 0 10 0 3 1 1 3 3 1
H 8
CX 1 5 1 6 1 8 1 9 1 10 1 11 1 13 1 14 1 15 1 19 1 20 2 1 3 1 4 1 8 1 9 1
H 7
CX 2 4 2 5 2 7 2 8 2 9 2 10 2 13 2 15 2 16 2 18 2 19 2 20 2 21 4 2 5 2 7 2 8 2 9 2 10 2 9 3 3 9 9 3 3 5 3 9 3 10 3 13 3 15 3 17 3 20 3 22 4 3 6 3 7 3 8 3 5 4 4 5 5 4 4 5 4 8 4 9 4 13 4 17 4 19 4 21 4 22 6 4 7 4 8 4 9 4 6 5 5 6 6 5 5 6 5 7 5 8 5 9 5 10 5 11 5 15 5 17 5 18 5 19 5 21 5 22 7 5 10 5 8 6 6 8 8 6 6 7 6 10 6 11 6 13 6 15 6 16 6 17 6 18 6 19 9 7 7 9 9 7 7 10 7 11 7 21 7 22 8 7 9 7 9 8 8 9 9 8 8 9 8 11 8 13 8 16 8 17 8 18 8 21 10 8 10 9 9 10 10 9 9 10 9 15 9 21 10 11 10 13 10 16 10 17 10 21 11 13 11 15 11 16 11 17 11 21 22 11 21 12 12 21 21 12 22 12 20 13 13 20 20 13 19 14 14 19 19 14 18 15 15 18 18 15 17 16 16 17 17 16 22 16 22 17 22 18 22 20
"""

def resynthesize():
    # 1. Parse baseline
    baseline = stim.Circuit(baseline_text)
    
    # 2. Simulate to get tableau
    # Since we want to reproduce the STATE, we care about the tableau that maps Z basis to the stabilizer state.
    # stim.TableauSimulator.do() updates the state.
    # We can get the tableau using current_inverse_tableau().inverse()
    sim = stim.TableauSimulator()
    sim.do(baseline)
    
    # The tableau T such that T|0> = |psi>.
    # Actually current_inverse_tableau() gives T^-1.
    # So we want T = sim.current_inverse_tableau().inverse()
    tableau = sim.current_inverse_tableau().inverse()
    
    # 3. Synthesize
    # method='graph_state' is generally best for CX count (uses CZs)
    candidate = tableau.to_circuit(method="graph_state")
    
    # Clean the circuit: replace RX with H, remove TICK
    new_circuit = stim.Circuit()
    for instruction in candidate:
        if instruction.name == "RX":
            # RX usually resets to X basis. For |0> input, this is equivalent to H |0> -> |+>
            # So we replace RX with H
            # But we must check if targets are correct.
            # RX targets are integers.
            # We construct H instruction.
            new_circuit.append("H", instruction.targets_copy())
        elif instruction.name == "TICK":
            continue
        else:
            new_circuit.append(instruction)
            
    return new_circuit

if __name__ == "__main__":
    cand = resynthesize()
    print(cand)
