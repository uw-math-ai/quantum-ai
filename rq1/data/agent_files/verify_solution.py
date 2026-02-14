import stim
import sys
import json

def check_circuit():
    with open("circuit_solution.stim", "r") as f:
        circuit_str = f.read()
    
    # Just print the circuit to stdout so I can grab it (or use it in tool call)
    # Actually I need to call the tool.
    # But I can't call tools from python script.
    # I will just verify it locally first.
    
    stabilizers_str = [
        "XZZXIIIIIIIIIIIIIIIIIIIII",
        "IIIIIXZZXIIIIIIIIIIIIIIII",
        "IIIIIIIIIIXZZXIIIIIIIIIII",
        "IIIIIIIIIIIIIIIXZZXIIIIII",
        "IIIIIIIIIIIIIIIIIIIIXZZXI",
        "IXZZXIIIIIIIIIIIIIIIIIIII",
        "IIIIIIXZZXIIIIIIIIIIIIIII",
        "IIIIIIIIIIIXZZXIIIIIIIIII",
        "IIIIIIIIIIIIIIIIXZZXIIIII",
        "IIIIIIIIIIIIIIIIIIIIIXZZX",
        "XIXZZIIIIIIIIIIIIIIIIIIII",
        "IIIIIXIXZZIIIIIIIIIIIIIII",
        "IIIIIIIIIIXIXZZIIIIIIIIII",
        "IIIIIIIIIIIIIIIXIXZZIIIII",
        "IIIIIIIIIIIIIIIIIIIIXIXZZ",
        "ZXIXZIIIIIIIIIIIIIIIIIIII",
        "IIIIIZXIXZIIIIIIIIIIIIIII",
        "IIIIIIIIIIZXIXZIIIIIIIIII",
        "IIIIIIIIIIIIIIIZXIXZIIIII",
        "IIIIIIIIIIIIIIIIIIIIZXIXZ",
        "XXXXXZZZZZZZZZZXXXXXIIIII",
        "IIIIIXXXXXZZZZZZZZZZXXXXX",
        "XXXXXIIIIIXXXXXZZZZZZZZZZ",
        "ZZZZZXXXXXIIIIIXXXXXZZZZZ"
    ]
    
    circuit = stim.Circuit(circuit_str)
    
    # Check stabilizers
    # We simulate the circuit and check if stabilizers have expectation +1
    
    # Convert circuit to Tableau
    # Note: State preparation circuit starting from |0>
    t = stim.Tableau.from_circuit(circuit)
    
    # Check each stabilizer
    all_good = True
    for s in stabilizers_str:
        p = stim.PauliString(s)
        # We need <psi| P |psi> = +1
        # |psi> = U |0>
        # <0| U^dag P U |0> = +1
        # Calculate P' = U^dag P U.
        # Actually P' = U^-1 P U.
        # stim.Tableau(P) gives the conjugation?
        # t(P) = U P U^dag.
        # So we want to know if U P U^dag stabilizes |0>? No.
        # If U|0> is stabilized by P, then P U |0> = U |0>.
        # => U^dag P U |0> = |0>.
        # So U^dag P U must be in the stabilizer group of |0> (i.e. Z operators).
        # We need to invert the tableau.
        
        t_inv = t.inverse()
        p_prime = t_inv(p)
        
        # Check if p_prime is Z-like and positive
        # p_prime must be a product of Zs with + sign
        # We check if it has any X or Y components
        
        # p_prime is a PauliString.
        # Check signs.
        if p_prime.sign != +1:
            print(f"Stabilizer {s} has -1 eigenvalue")
            all_good = False
            continue

        # Check for X or Y components.
        # We can convert to numpy
        xs, zs = p_prime.to_numpy()
        if np.any(xs):
            print(f"Stabilizer {s} not preserved (mapped to non-Z)")
            all_good = False
            
    if all_good:
        print("All stabilizers preserved!")
    else:
        print("Some stabilizers failed.")

if __name__ == "__main__":
    check_circuit()
