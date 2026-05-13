
import pathlib
lines = pathlib.Path('candidate.stim').read_text().splitlines()
print("PART 2")
print('\n'.join(lines[600:1200]))
print("END PART 2")
