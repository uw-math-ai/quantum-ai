import numpy as np

def generate_stabilizers(physical_qubits: int, logical_qubits: int) -> list[str]:
    """Generate stabilizers for a given number of physical and logical qubits.

    Args:
        physical_qubits (int): Number of physical qubits.
        logical_qubits (int): Number of logical qubits.

    Returns:
        list[str]: List of stabilizer strings.
    """
    required_stabilizers = physical_qubits - logical_qubits
    stabilizers = np.array([[0]])
    while (not np.any(stabilizers != 0)
           or np.count_nonzero(stabilizers[0][:physical_qubits] + stabilizers[0][physical_qubits:]) < 2):
        stabilizers = np.random.randint(0, 2, size=(1, 2 * physical_qubits))
    N = np.identity(2 * physical_qubits, dtype=int) # Row(N) = Null(stabilizers)
    j = np.argmax(stabilizers[0])
    N += N[j]
    N = np.delete(N, j, axis=0)

    I = np.identity(physical_qubits, dtype=int)
    M_0 = np.zeros((physical_qubits, physical_qubits), dtype=int)

    # [0 I]
    # [I 0]
    M_swap = np.concatenate((np.concatenate((M_0, I), axis=1), np.concatenate((I, M_0), axis=1)), axis=0)
    for _ in range(required_stabilizers - 1):
        while True:
            new_stabilizer = np.random.randint(0, 2, size=(1, 2 * physical_qubits))
            if (np.count_nonzero(new_stabilizer[0][:physical_qubits] + new_stabilizer[0][physical_qubits:]) >= 2 # checks non-trivial
                and np.all(stabilizers @ (M_swap @ new_stabilizer.T) % 2 == 0)): # checks commutation
                prod = N @ new_stabilizer.T
                if np.any(prod != 0): # checks linear independence
                    j = np.argmax(prod)
                    N += N[j]
                    N = np.delete(N, j, axis=0)
                    stabilizers = np.concatenate((stabilizers, new_stabilizer), axis=0)
                    break
    
    def map_fn(stabilizer: np.ndarray) -> str:
        pauli_map = { (0,0): 'I', (1,0): 'X', (0,1): 'Z', (1,1): 'Y' }
        pauli_string = ''
        for i in range(physical_qubits):
            x = stabilizer[i]
            z = stabilizer[i + physical_qubits]
            pauli_string += pauli_map[(x, z)]
        return pauli_string
    
    print(np.sum(M_swap @ stabilizers.T, axis=1) >= 1)
    
    stabilizer_strings = [map_fn(stabilizer) for stabilizer in stabilizers]
    return stabilizer_strings

if __name__ == "__main__":
    physical_qubits = 5
    logical_qubits = 1
    stabilizers = generate_stabilizers(physical_qubits, logical_qubits)
    for stab in stabilizers:
        print(stab)