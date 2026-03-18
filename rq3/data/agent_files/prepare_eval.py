import stim
import json

def eval_raw():
    with open("candidate_raw.stim", "r") as f:
        cand = f.read()
    print("Candidate read.")
    # I can't call evaluate_optimization from python directly.
    # I have to do it via tool call.

if __name__ == "__main__":
    eval_raw()
