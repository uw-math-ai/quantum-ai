
import pathlib
lines = pathlib.Path('candidate.stim').read_text().splitlines()
print("PART 4")
print('\n'.join(lines[1800:]))
print("END PART 4")
