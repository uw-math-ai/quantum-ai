import solve_175_new
import json

output = {
    "circuit": open("circuit_175.stim").read(),
    "stabilizers": solve_175_new.stabilizers
}

print(json.dumps(output))
