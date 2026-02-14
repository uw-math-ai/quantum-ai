import sys

def analyze_stabilizers(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    n_qubits = len(lines[0])
    n_stabs = len(lines)
    print(f"Number of qubits: {n_qubits}")
    print(f"Number of stabilizers: {n_stabs}")

    # Check for block structure
    block_size = 23
    num_blocks = n_qubits // block_size
    
    if n_qubits % block_size != 0:
        print(f"Warning: {n_qubits} is not divisible by {block_size}")
        return

    print(f"Checking for {num_blocks} blocks of size {block_size}")
    
    blocks = [[] for _ in range(num_blocks)]
    
    for line in lines:
        # Check if the stabilizer is local to one block
        active_blocks = []
        for i in range(num_blocks):
            sub_str = line[i*block_size : (i+1)*block_size]
            if sub_str != 'I' * block_size:
                active_blocks.append(i)
        
        if len(active_blocks) == 0:
            print("Warning: Stabilizer is all Identity")
        elif len(active_blocks) == 1:
            block_idx = active_blocks[0]
            sub_str = line[block_idx*block_size : (block_idx+1)*block_size]
            blocks[block_idx].append(sub_str)
        else:
            print(f"Stabilizer spans multiple blocks: {active_blocks}")
            # print(line)

    for i, block_stabs in enumerate(blocks):
        print(f"Block {i}: {len(block_stabs)} stabilizers")
        # if i == 0:
        #     for s in block_stabs:
        #         print(s)
        
    # Check if all blocks are identical
    base_block = set(blocks[0])
    for i in range(1, num_blocks):
        current_block = set(blocks[i])
        if base_block != current_block:
            print(f"Block {i} is different from Block 0")
            diff = base_block.symmetric_difference(current_block)
            print(f"Difference: {diff}")
        else:
            print(f"Block {i} is identical to Block 0")

    # Print stabilizers of Block 0 to a file for solving
    with open('block_stabilizers_23.txt', 'w') as f:
        for s in blocks[0]:
            f.write(s + '\n')

if __name__ == "__main__":
    analyze_stabilizers('stabilizers_184.txt')
