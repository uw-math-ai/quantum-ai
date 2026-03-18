import stim
with open('cleaned_candidate.stim', 'r') as f:
    c = stim.Circuit(f.read())
print(str(c))
