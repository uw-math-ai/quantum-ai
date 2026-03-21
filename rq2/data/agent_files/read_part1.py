
import pathlib
lines = pathlib.Path('candidate.stim').read_text().splitlines()
print("PART 1")
print('\n'.join(lines[0:600]))
print("END PART 1")
