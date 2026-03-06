import stim
with open("candidate_graph_state.stim", "r") as f:
    c = stim.Circuit(f.read())
    for instr in c:
        args = []
        for t in instr.targets_copy():
            args.append(str(t.value))
        
        # print in chunks
        print(f"{instr.name}", end=" ")
        for i, arg in enumerate(args):
            print(arg, end=" ")
            if (i + 1) % 20 == 0:
                print("\n", end="")
        print("") # end of instruction
