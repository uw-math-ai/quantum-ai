import stim
try:
    s = stim.PauliString('XX')
    print('Created PauliString')
    t = stim.Tableau.from_stabilizers([s], allow_redundant=True, allow_underconstrained=True)
    print('Created Tableau from PauliString list')
except Exception as e:
    print(f'Error 1: {e}')

try:
    t = stim.Tableau.from_stabilizers(['XX'], allow_redundant=True, allow_underconstrained=True)
    print('Created Tableau from str list')
except Exception as e:
    print(f'Error 2: {e}')

