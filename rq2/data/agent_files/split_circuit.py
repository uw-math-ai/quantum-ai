import stim
import sys

def split_circuit(input_path, output_path):
    with open(input_path, 'r') as f:
        c = stim.Circuit(f.read())
        
    with open(output_path, 'w') as f:
        for op in c.flattened():
            name = op.name
            targets = op.targets_copy()
            if name in ["CX", "SWAP", "CZ", "ISWAP"]:
                # Split into pairs
                pairs = []
                for k in range(0, len(targets), 2):
                    pairs.append((targets[k], targets[k+1]))
                
                # Write each pair on a new line
                for p in pairs:
                    t1 = p[0].value
                    t2 = p[1].value
                    f.write(f"{name} {t1} {t2}\n")
            elif name in ["H", "S", "X", "Y", "Z", "I"]:
                # Split into singles
                for t in targets:
                    val = t.value
                    f.write(f"{name} {val}\n")
            elif name == "M":
                # Split into singles?
                # Or small groups
                group_size = 10
                t_vals = [t.value for t in targets]
                for i in range(0, len(t_vals), group_size):
                    chunk = t_vals[i:i+group_size]
                    s = " ".join(str(x) for x in chunk)
                    f.write(f"M {s}\n")
            else:
                f.write(str(op) + "\n")
                
    print(f"Split circuit written to {output_path}")

if __name__ == "__main__":
    split_circuit("candidate_fixed_v3.stim", "candidate_final.stim")
