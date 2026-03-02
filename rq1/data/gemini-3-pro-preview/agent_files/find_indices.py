suffixes = [
    "XIIXIIIIIIIIIXX",
    "ZIIZIIIIIIIIIZZ",
    "ZIIIIIIIIZIZIIIIIIIIIIIIIIIIZIIIIII",
    "XIXXIXXIIXIIXIIIIIIIIIIIIIIIIII"
]

with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_148.txt', 'r') as f:
    lines = [line.strip() for line in f if line.strip()]

for suffix in suffixes:
    found = False
    for i, line in enumerate(lines):
        if line.endswith(suffix):
            print(f"Suffix '{suffix}' found at index {i}")
            found = True
            break
    if not found:
        print(f"Suffix '{suffix}' not found")
