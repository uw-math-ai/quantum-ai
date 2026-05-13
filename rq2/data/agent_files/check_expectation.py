import stim

def check_expectation():
    with open("data/gemini-3-pro-preview/agent_files_ft/original.stim", "r") as f:
        circuit = stim.Circuit(f.read())
        
    sim = stim.TableauSimulator()
    sim.do(circuit)
    
    # Logical op string
    # -_______________XXX______XXX_________Z___Z___Z
    # Convert to PauliString
    # The output format of PauliString in previous script used `_` for I.
    # But PauliString constructor takes `I`, `X`, `Y`, `Z`.
    # I'll manually construct it.
    
    # Indices from previous thought:
    # 15,16,17 X
    # 24,25,26 X
    # 36 Z
    # 40 Z
    # 44 Z
    
    op = stim.PauliString(45)
    for k in [15,16,17,24,25,26]: op[k] = 1 # X
    for k in [36,40,44]: op[k] = 3 # Z
    
    # Check expectation
    res = sim.peek_observable_expectation(op)
    print(f"Expectation of Logical Op: {res}")

if __name__ == "__main__":
    check_expectation()
