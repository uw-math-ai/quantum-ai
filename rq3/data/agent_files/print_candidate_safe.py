import stim

def main():
    with open("candidate_split.stim", "r") as f:
        circuit = stim.Circuit(f.read())
    
    for instr in circuit:
        print(instr)

if __name__ == "__main__":
    main()
