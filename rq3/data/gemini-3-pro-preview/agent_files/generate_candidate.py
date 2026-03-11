import stim
import sys

def main():
    try:
        # 1. Read stabilizers
        with open(r'C:\Users\anpaz\Repos\quantum-ai\rq3\data\gemini-3-pro-preview\agent_files\stabilizers_correct.txt', 'r') as f:
            # Handle Windows line endings by replacing \r too
            raw_text = f.read().replace('\n', '').replace('\r', '').replace(' ', '')
        
        stabilizers = [s for s in raw_text.split(',') if s]
        print(f'Loaded {len(stabilizers)} stabilizers.', file=sys.stderr)
        
        if not stabilizers:
            print('No stabilizers loaded!', file=sys.stderr)
            return

        print(f'First raw stabilizer: {stabilizers[0]!r}', file=sys.stderr)

        # Convert to stim.PauliString
        stim_stabilizers = []
        for i, s in enumerate(stabilizers):
            try:
                ps = stim.PauliString(s)
                stim_stabilizers.append(ps)
            except Exception as e:
                print(f'Error parsing stabilizer {i} ({s!r}): {e}', file=sys.stderr)
                return

        print(f'First PauliString type: {type(stim_stabilizers[0])}', file=sys.stderr)

        # 2. Create Tableau
        try:
            # Ensure allow_underconstrained is passed as kwarg or positionally correct
            # stim version check?
            print(f'Calling from_stabilizers with list of {len(stim_stabilizers)} PauliStrings', file=sys.stderr)
            tableau = stim.Tableau.from_stabilizers(stim_stabilizers, allow_underconstrained=True)
            print('Tableau created successfully.', file=sys.stderr)
        except Exception as e:
            print(f'Error creating tableau: {e}', file=sys.stderr)
            # Maybe fallback to not using allow_underconstrained if it's the issue (unlikely)
            return

        # 3. Synthesize Circuit (Graph State)
        try:
            circuit = tableau.to_circuit(method='graph_state')
            print('Circuit synthesized successfully.', file=sys.stderr)
        except Exception as e:
            print(f'Error synthesizing circuit: {e}', file=sys.stderr)
            return
        
        # 4. Clean up RX gates
        circuit_str = str(circuit)
        
        new_lines = []
        for line in circuit_str.splitlines():
            stripped = line.strip()
            if stripped.startswith('RX'):
                targets = stripped[2:].strip()
                new_lines.append(f'H {targets}')
            elif stripped.startswith('M'):
                 pass 
            else:
                new_lines.append(line)
        
        final_circuit_str = '\n'.join(new_lines)
        print(final_circuit_str)
        
    except Exception as e:
        print(f'Failed: {e}', file=sys.stderr)

if __name__ == '__main__':
    main()
