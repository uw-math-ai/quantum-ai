import stim

def main():
    with open("data/final_candidate.stim", "r") as f:
        c = stim.Circuit(f.read())
    
    # Stim's __str__ method usually formats nicely, but might produce long lines.
    # We can iterate instructions and print them.
    
    with open("data/safe_candidate.stim", "w") as f:
        for instruction in c:
            # Print instruction name
            f.write(instruction.name)
            # Targets
            targets = instruction.targets_copy()
            # If args, print them (graph state usually doesn't have args)
            args = instruction.gate_args_copy()
            
            if args:
                f.write("(")
                f.write(",".join(str(a) for a in args))
                f.write(")")
            
            # Print targets in chunks
            # e.g. 10 targets per line
            count = 0
            for t in targets:
                # Use t.repr() or manually handle
                if t.is_qubit_target:
                    f.write(" " + str(t.value))
                else:
                    f.write(" " + str(t))
                count += 1
                if count % 15 == 0:
                    f.write("\n") # Newline after 15 targets
            f.write("\n") # Newline after instruction

    print("Reformatted to data/safe_candidate.stim")

if __name__ == "__main__":
    main()
