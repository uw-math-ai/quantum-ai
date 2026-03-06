import stim
import sys

def main():
    try:
        with open("best_candidate.stim", "r") as f:
            circ = stim.Circuit(f.read())
    except Exception as e:
        print(f"Could not load best_candidate.stim: {e}")
        return

    new_circ = stim.Circuit()
    for instruction in circ:
        if instruction.name == "RX":
            new_circ.append("H", instruction.targets_copy())
        elif instruction.name == "TICK":
            new_circ.append("TICK")
        else:
            new_circ.append(instruction)

    cx_count = new_circ.count_determined_measurements() # Dummy call to check if object is valid
    # cx_count = new_circ.num_gates("CX") # This failed
    
    with open("candidate_v99.stim", "w") as f:
        f.write(str(new_circ))
    print("Saved candidate_v99.stim")

if __name__ == "__main__":
    main()
