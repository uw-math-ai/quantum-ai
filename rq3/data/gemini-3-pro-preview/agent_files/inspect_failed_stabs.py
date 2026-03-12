import stim

with open('current_task_stabilizers.txt', 'r') as f:
    lines = [l.strip() for l in f.readlines() if l.strip()]

idx = [9, 84]
for i in idx:
    print(f'Stabilizer {i}: {lines[i]}')
    
    # Check expectation in baseline
    try:
        p = stim.PauliString(lines[i])
        with open('current_task_baseline.stim', 'r') as f:
            c = stim.Circuit(f.read())
        sim = stim.TableauSimulator()
        sim.do(c)
        exp = sim.peek_observable_expectation(p)
        print(f'Expectation: {exp}')
    except Exception as e:
        print(f'Error: {e}')
