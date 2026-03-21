
import pathlib
lines = pathlib.Path('candidate.stim').read_text().splitlines()
for i in range(0, len(lines), 500):
    print(f"--- CHUNK {i} ---")
    print('\n'.join(lines[i:i+500]))
