import stim
import sys

target_stabilizers_str = [
    "IIXIXXXIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIXIXXXIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIXIXXXIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIXIXXXIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXXX", "IXIXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIXIXIXXIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIXIXIXXIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIXIXIXXIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIXIXX", "XXXIIXIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIXXXIIXIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIXXXIIXIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIXXXIIXIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXIIXI", "IIZIZZZIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIZIZZZIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIZIZZZIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIZIZZZIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZZZ", "IZIZIZZIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIZIZIZZIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIZIZIZZIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIZIZIZZIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZIZZ", "ZZZIIZIIIIIIIIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIZZZIIZIIIIIIIIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIZZZIIZIIIIIIIIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIZZZIIZIIIIIIII", "IIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZIIZI", "XXIXIIIZZIZIIIZZIZIIIXXIXIIIIIIIIII", "IIIIIIIXXIXIIIZZIZIIIZZIZIIIXXIXIII", "XXIXIIIIIIIIIIXXIXIIIZZIZIIIZZIZIII", "ZZIZIIIXXIXIIIIIIIIIIXXIXIIIZZIZIII"
]

def main():
    try:
        # Load candidate
        # The file is candidate.stim
        with open('candidate.stim', 'r') as f:
            lines = f.readlines()
        
        # Manually parse/modify to avoid stim.Circuit immutable issues
        # Actually stim.Circuit is mutable if we append to new one
        c = stim.Circuit.from_file('candidate.stim')
        new_c = stim.Circuit()
        
        for op in c:
            if op.name == 'RX':
                # Replace RX with H
                new_c.append('H', op.targets_copy())
            elif op.name == 'R':
                # Remove R if input is |0>
                pass
            elif op.name == 'TICK':
                pass # remove ticks
            else:
                new_c.append(op)
        
        # Verify
        stabilizers = [stim.PauliString(s) for s in target_stabilizers_str]
        sim = stim.TableauSimulator()
        sim.do_circuit(new_c)
        valid = True
        for s in stabilizers:
            if sim.peek_observable_expectation(s) != 1:
                valid = False
                break
        
        if valid:
            print("Verified valid.")
            with open("final.stim", "w") as f:
                f.write(str(new_c))
        else:
            print("INVALID after modification.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
