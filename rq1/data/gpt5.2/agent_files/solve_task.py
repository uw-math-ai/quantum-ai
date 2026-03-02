import stim

def solve():
    with open('stabilizers_task.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    stabilizers = []
    for line in lines:
        stabilizers.append(stim.PauliString(line))

    print(f'Loaded {len(stabilizers)} stabilizers.')
    if stabilizers:
        print(f'Stabilizer length: {len(stabilizers[0])}')

    # Check for anticommutativity
    anticommuting_pairs = []
    for i in range(len(stabilizers)):
        for j in range(i + 1, len(stabilizers)):
            if stabilizers[i].commutes(stabilizers[j]) == False:
                anticommuting_pairs.append((i, j))

    if anticommuting_pairs:
        print(f'Found {len(anticommuting_pairs)} anticommuting pairs.')
        for i, j in anticommuting_pairs[:5]:
            print(f'  {i} and {j} anticommute')
    else:
        print('All stabilizers commute.')
        # Proceed to solve
        try:
            tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True)
            circuit = tableau.to_circuit('elimination')
            with open('circuit_task.stim', 'w') as f:
                f.write(str(circuit))
            print('Circuit generated.')
            
            # Verify locally
            print('Verifying locally...')
            sim = stim.TableauSimulator()
            sim.do(circuit)
            failed = False
            for i, stab in enumerate(stabilizers):
                expectation = sim.peek_observable_expectation(stab)
                if expectation != 1:
                    print(f'Stabilizer {i} failed: expectation {expectation}')
                    failed = True
            if not failed:
                print('Verification finished successfully.')

        except Exception as e:
            print(f'Error generating circuit: {e}')

if __name__ == '__main__':
    solve()
