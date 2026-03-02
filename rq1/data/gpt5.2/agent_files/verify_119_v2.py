import stim
import sys

def verify():
    filename = r'data\gemini-3-pro-preview\agent_files\stabilizers_119.txt'
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    fixed = []
    for line in lines:
        if len(line) == 121:
            new_line = 'I'*69 + 'ZIIZIIIIIZIIZ' + 'I'*37
            fixed.append(stim.PauliString(new_line))
        else:
            fixed.append(stim.PauliString(line))
            
    try:
        # Create Tableau
        # allow_redundant=True, allow_underconstrained=True
        # This will create a tableau that stabilizes the stabilizers.
        # But if they are inconsistent, it will fail.
        # If they are consistent but redundant, it should satisfy all.
        
        print("Creating Tableau...")
        tableau = stim.Tableau.from_stabilizers(fixed, allow_redundant=True, allow_underconstrained=True)
        inv = tableau.inverse()
        
        indices = [6, 20, 27, 34, 41, 48, 55, 62, 83, 90, 111]
        
        failures = 0
        for idx in indices:
            p = fixed[idx]
            res = inv(p) # This applies inv to p.
            s = str(res)
            # Stim string format: "+Z_Z__"
            # It should not have X or Y.
            if 'X' in s or 'Y' in s:
                # If it has X or Y, it means it doesn't stabilize |0>.
                # Unless the X/Y is on a qubit that is not in the stabilizer set (gauge)?
                # No, if P stabilizes the state, T^-1 P T |0> = |0>.
                # |0> is stabilized by Z_i.
                # So T^-1 P T must be product of Z_i.
                # So it must be Z-type.
                print(f"Index {idx} failed: transformed to {s} (has X/Y)")
                failures += 1
            elif s.startswith('-'):
                print(f"Index {idx} failed: transformed to {s} (phase -1)")
                failures += 1
            else:
                print(f"Index {idx} passed: transformed to {s}")
                
        print(f"Total failures: {failures}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify()
