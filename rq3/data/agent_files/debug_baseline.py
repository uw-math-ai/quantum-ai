with open(r'C:\Users\anpaz\Repos\quantum-ai\rq3\baseline_prompt.stim', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.strip().startswith('CX 50'):
        print(f"Line {i+1}: {line.strip()}")
        parts = line.strip().split()
        args = parts[1:]
        print(f"Number of args: {len(args)}")
        if len(args) % 2 != 0:
            print("ODD NUMBER OF ARGS!")
