import stim

def solve():
    with open("stabilizers_155.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"Read {len(lines)} lines from stabilizers_155.txt")
    
    stabilizers = []
    for line in lines:
        try:
            stabilizers.append(stim.PauliString(line))
        except Exception as e:
            print(f"Error parsing line: {line}\n{e}")
            return

    # Check for consistency?
    # Actually, let's just try to build the tableau.
    try:
        # We allow underconstrained because maybe they didn't provide 155 independent generators.
        # We allow redundant because maybe there are dependent generators.
        tableau = stim.Tableau.from_stabilizers(stabilizers, allow_underconstrained=True, allow_redundant=True)
        
        # Verify locally
        # The tableau represents a state |psi>
        # We need to check if S |psi> = |psi> for all S in stabilizers.
        # stim.TableauSimulator() starts in |0...0>
        # applying tableau operations prepares the state.
        
        # Convert to circuit
        circuit = tableau.to_circuit("elimination")
        
        print("Circuit generated.")
        
        # Verify
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        # Check expectation values
        valid = True
        for i, s in enumerate(stabilizers):
            if sim.peek_observable_expectation(s) != 1:
                print(f"Stabilizer {i} not satisfied: {s}")
                valid = False
                # If it's -1, we might need to fix sign, but usually from_stabilizers handles signs if included in PauliString
                # But here the strings in file don't have signs, so they default to +1.
                # If peek returns -1, it means the state is a -1 eigenstate.
                # If peek returns 0, it means it's not an eigenstate (indefinite).
        
        if valid:
            print("All stabilizers satisfied.")
            with open("circuit_155.stim", "w") as f:
                f.write(str(circuit))
        else:
            print("Some stabilizers not satisfied.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve()
