import stim

def read_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip().replace(',', '') for line in f if line.strip()]
    return [stim.PauliString(s) for s in lines]

def main():
    stabilizers = read_stabilizers('data/gemini-3-pro-preview/agent_files/stabilizers_184.txt')
    
    print("Stabilizers 30-34:")
    for i in range(30, 35):
        if 0 <= i < len(stabilizers):
            print(f"{i}: {stabilizers[i]}")
            # indices of X and Z
            x_indices = [k for k, p in enumerate(stabilizers[i]) if p == 1 or p == 2] # X=1, Y=2
            z_indices = [k for k, p in enumerate(stabilizers[i]) if p == 3 or p == 2] # Z=3, Y=2
            print(f"  X: {x_indices}")
            print(f"  Z: {z_indices}")

    print("\nStabilizer 32 anticommutes with:")
    anticommuting = [88, 96, 112, 120, 136, 144, 152, 160]
    for i in anticommuting:
        print(f"{i}: {stabilizers[i]}")
        x_indices = [k for k, p in enumerate(stabilizers[i]) if p == 1 or p == 2]
        z_indices = [k for k, p in enumerate(stabilizers[i]) if p == 3 or p == 2]
        print(f"  X: {x_indices}")
        print(f"  Z: {z_indices}")
        
        # Check where they overlap
        overlap = []
        s32 = stabilizers[32]
        si = stabilizers[i]
        for k in range(len(s32)):
            p32 = s32[k]
            pi = si[k]
            if p32 != 0 and pi != 0 and p32 != pi:
                overlap.append(k)
        print(f"  Overlap with 32: {overlap} (count: {len(overlap)})")

if __name__ == "__main__":
    main()
