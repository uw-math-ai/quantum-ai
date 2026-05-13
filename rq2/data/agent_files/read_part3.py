
import pathlib
lines = pathlib.Path('candidate.stim').read_text().splitlines()
print("PART 3")
print('\n'.join(lines[1200:1800]))
print("END PART 3")
