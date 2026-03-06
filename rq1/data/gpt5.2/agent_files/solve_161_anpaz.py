import stim
import sys

def solve():
    print("Reading stabilizers from v3...")
    with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq1\\stabilizers_161_v3.txt") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    # Verify lengths
    for i, line in enumerate(lines):
        if len(line) != 161:
            print(f"Error: Stabilizer {i} has length {len(line)}, expected 161.")
            return

    print(f"Read {len(lines)} stabilizers.")

    print("Attempting to generate tableau from stabilizers...")
    try:
        # Create a tableau from the stabilizers
        # allow_underconstrained=True because we might not have a full set of 161 stabilizers
        # allow_redundant=True in case there are dependent stabilizers
        tableau = stim.Tableau.from_stabilizers(
            [stim.PauliString(s) for s in lines],
            allow_underconstrained=True,
            allow_redundant=True
        )
        
        # Convert to circuit
        circuit = tableau.to_circuit("elimination")
        
        print("Circuit generated successfully.")
        
        # Verify the circuit against the stabilizers locally
        print("Verifying circuit locally...")
        sim = stim.TableauSimulator()
        sim.do(circuit)
        
        # Check if the state satisfies the stabilizers
        all_good = True
        num_satisfied = 0
        for i, s_str in enumerate(lines):
            s = stim.PauliString(s_str)
            expectation = sim.peek_observable_expectation(s)
            if expectation != 1:
                # print(f"Stabilizer {i} not satisfied: {s_str}")
                all_good = False
            else:
                num_satisfied += 1
        
        print(f"Satisfied {num_satisfied}/{len(lines)} stabilizers locally.")
        
        if all_good:
            print("All stabilizers satisfied locally!")
        else:
            print("Some stabilizers not satisfied locally.")
            
        with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq1\\circuit_161_v3.stim", "w") as f:
            f.write(str(circuit))
            
    except Exception as e:
        print(f"Error generating circuit: {e}")

if __name__ == "__main__":
    solve()
