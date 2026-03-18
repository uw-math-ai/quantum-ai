import stim

def check_cx_count():
    try:
        with open("candidate_elimination.stim", "r") as f:
            circ = f.read()
        print(f"Elimination CX count: {circ.count('CX')}")
    except Exception as e:
        print(f"Error reading elimination circuit: {e}")

    try:
        with open("baseline_current.stim", "r") as f:
            base = f.read()
        print(f"Baseline CX count: {base.count('CX')}")
    except Exception as e:
        print(f"Error reading baseline: {e}")

    try:
        with open("candidate_opt_graph_v3.stim", "r") as f:
            opt = f.read()
        print(f"Optimized V3 CX count: {opt.count('CX')}")
    except Exception as e:
        print(f"Error reading optimized V3: {e}")

if __name__ == "__main__":
    check_cx_count()
