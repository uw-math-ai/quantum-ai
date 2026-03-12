import stim
c = stim.Circuit.from_file("candidate_final_submission.stim")
print(f"CX count: {sum(1 for op in c if op.name == 'CX')}")
print(f"CZ count: {sum(1 for op in c if op.name == 'CZ')}")
print(f"CX gates: {[op for op in c if op.name == 'CX']}")
