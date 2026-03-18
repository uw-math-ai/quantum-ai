import stim

def main():
    try:
        with open('baseline_job.stim', 'r') as f:
            baseline_text = f.read()
        baseline = stim.Circuit(baseline_text)
        
        sim = stim.TableauSimulator()
        sim.do(baseline)
        tableau = sim.current_inverse_tableau().inverse()
        circuit = tableau.to_circuit(method='graph_state')
        
        # Iterate and print split
        for instr in circuit:
            if instr.name == "RX":
                for t in instr.targets_copy():
                    print(f"H {t.value}")
            elif instr.name == "CZ":
                targets = instr.targets_copy()
                for i in range(0, len(targets), 2):
                    print(f"CZ {targets[i].value} {targets[i+1].value}")
            elif instr.name == "TICK":
                print("TICK")
            else:
                name = instr.name
                targets = instr.targets_copy()
                args = instr.gate_args_copy()
                
                gate_len = 1
                if name in ["CX", "CNOT", "SWAP", "ISWAP", "CZ"]: gate_len = 2
                
                for i in range(0, len(targets), gate_len):
                    sub_targets = targets[i:i+gate_len]
                    t_str = " ".join(str(t.value) for t in sub_targets)
                    
                    if args:
                        arg_str = "(" + ",".join(str(a) for a in args) + ")"
                        print(f"{name}{arg_str} {t_str}")
                    else:
                        print(f"{name} {t_str}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
