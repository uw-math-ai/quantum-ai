import stim
import numpy as np

def get_block_stabilizers():
    return [
        "IXIIXIIXXXXXIIIIIIIIIIX",
        "XIIXIIXXXXXIIIIIIIIIIXI",
        "IXXIXXXIIIXXIIIIIIIIXII",
        "XXIXXXIIIXXIIIIIIIIXIII",
        "XXXXIIXIIXXIIIIIIXIIIII",
        "XIXIXIXXXIIXIIIIIXIIIII",
        "IIIXXXXIXXIXIIIIXIIIIII",
        "IIXXXXIXXIXIIIIXIIIIIII",
        "IXXXXIXXIXIIIIXIIIIIIII",
        "XXXXIXXIXIIIIXIIIIIIIII",
        "XIXIIXIIXXXXXIIIIIIIIII",
        
        "IZIIZIIZZZZZIIIIIIIIIIZ",
        "ZIIZIIZZZZZIIIIIIIIIIZI",
        "IZZIZZZIIIZZIIIIIIIIZII",
        "ZZIZZZIIIZZIIIIIIIIZIII",
        "ZZZZIIIZIIZZIIIIIIZIIII",
        "ZIZIZIZZZIIZIIIIIZIIIII",
        "IIIZZZZIZZIZIIIIZIIIIII",
        "IIZZZZIZZIZIIIIZIIIIIII",
        "IZZZZIZZIZIIIIZIIIIIIII",
        "ZZZZIZZIZIIIIZIIIIIIIII",
        "ZIZIIZIIZZZZZIIIIIIIIII"
    ]

def get_global_parts():
    # Parts of global stabilizers on one block
    return [
        "XXIIIXXXIXIXIIIIIIIIIII",
        "ZZIIIZZZIZIZIIIIIIIIIII"
    ]

def solve():
    block_stabs = get_block_stabilizers()
    num_qubits = len(block_stabs[0])
    
    # We want to find a full set of stabilizers + logical operators.
    # We can do this by Gaussian elimination on the check matrix.
    
    # Construct check matrix
    # Rows: 22 stabilizers
    # Cols: 2 * 23 (X and Z)
    
    n = num_qubits
    m = len(block_stabs)
    
    xs = np.zeros((m, n), dtype=bool)
    zs = np.zeros((m, n), dtype=bool)
    
    for i, s in enumerate(block_stabs):
        for j, c in enumerate(s):
            if c == 'X': xs[i, j] = 1
            elif c == 'Z': zs[i, j] = 1
            elif c == 'Y': xs[i, j] = 1; zs[i, j] = 1
            
    tableau = stim.Tableau.from_stabilizers([stim.PauliString(s) for s in block_stabs], allow_redundant=True, allow_underconstrained=True)
    
    # Now let's see what the logical operators are.
    # The tableau has z_output acting as stabilizers.
    # The x_output acting as destabilizers?
    # Stim's `from_stabilizers` returns a Tableau that prepares the state stabilized by the given stabilizers.
    # It fills in the remaining degrees of freedom with arbitrary stabilizers (usually Z on the logical qubits).
    
    # So if we use this tableau to initialize a simulator, we are in the +1 eigenstate of the provided stabilizers.
    # The remaining degrees of freedom correspond to logical qubits.
    # We can inspect the tableau to find the logical operators.
    
    # But wait, `from_stabilizers` might pick a specific state for the logical qubits.
    # We want to know WHAT that state is relative to our global stabilizers.
    
    # Let's check the expectation value of the global parts on this state.
    
    global_parts = get_global_parts()
    
    sim = stim.TableauSimulator()
    sim.set_inverse_tableau(tableau.inverse()) # Initialize to the state
    
    print("Checking global parts on the default state prepared by tableau:")
    for i, gp in enumerate(global_parts):
        res = sim.peek_observables_expectation([stim.PauliString(gp)])
        print(f"Global part {i}: {gp} -> {res}")
        
    # This tells us if the default state is a +1 or -1 eigenstate or 0 (not stabilized).
    # If it's 0, it means it's a logical operator.
    
    # Also, we can find the logical operators explicitly.
    # They are the observables that commute with all stabilizers but are not in the stabilizer group.
    
if __name__ == "__main__":
    solve()
