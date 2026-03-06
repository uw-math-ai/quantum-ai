import textwrap
import sys

def reformat_stim(filename):
    with open(filename, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    for line in lines:
        if not line:
            continue
        tokens = line.split()
        if not tokens:
            continue
            
        current_line = []
        current_len = 0
        for token in tokens:
            if current_len + len(token) + 1 > 80:
                print(' '.join(current_line))
                current_line = [token]
                current_len = len(token)
            else:
                current_line.append(token)
                current_len += len(token) + 1
        if current_line:
            print(' '.join(current_line))

if __name__ == "__main__":
    reformat_stim("candidate.stim")