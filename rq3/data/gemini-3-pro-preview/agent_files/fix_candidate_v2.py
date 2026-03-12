import sys

try:
    with open('candidate.stim', 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('TICK'):
            continue
        # Replace RX with H at the start of the line
        if line.startswith('RX '):
            line = 'H ' + line[3:]
        
        # Also replace R with Reset, but here we don't have R.
        # We only have RX.
        
        new_lines.append(line)
        
    with open('candidate_fixed.stim', 'w') as f:
        f.write('\n'.join(new_lines))
        
    print(f'Fixed candidate written to candidate_fixed.stim with {len(new_lines)} lines.')

except Exception as e:
    print(f'Error: {e}')
