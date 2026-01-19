def generate_honeycomb_color_code(d: int) -> list[str]:
    """Generate stabilizers for the honeycomb color code of distance d.

    Args:
        d (int): Distance of the code (odd and >= 3).
    Returns:
        list[str]: List of stabilizer strings.
    """
    assert d % 2 == 1 and d >= 3, "Distance d must be an odd integer greater than or equal to 3."
    qubits = dict()
    hex_faces = []
    qubit_count = 0

    for row in range(d + 1):
        for col in range(2 * d + 2):
            if row == d:
                qubits[(row, col)] = qubits[(0, col)]
            elif col >= 2 * d:
                qubits[(row, col)] = qubits[(row, col % (2 * d))]
            else:
                qubits[(row, col)] = qubit_count
                qubit_count += 1
    
    stabilizers = []
    for row in range(d):
        for col in range(1, 2 * d + 1, 2):
            pauli_x = ['I'] * qubit_count
            pauli_z = ['I'] * qubit_count
            qs = [
                (row, col),
                (row, col + 1),
                (row, col + 2),
                (row + 1, col - 1),
                (row + 1, col),
                (row + 1, col + 1),
            ]
            for q in qs:
                pauli_x[qubits[q]] = 'X'
                pauli_z[qubits[q]] = 'Z'
            
            stabilizers.append(''.join(pauli_x))
            stabilizers.append(''.join(pauli_z))
    
    stabilizers.pop()

    return stabilizers

def generate_triangle_color_code(d: int) -> list[str]:
    """Generate stabilizers for the triangle color code of distance d.

    Args:
        d (int): Distance of the code (odd and >= 3).
    Returns:
        list[str]: List of stabilizer strings.
    """
    assert d % 2 == 1 and d >= 3, "Distance d must be an odd integer greater than or equal to 3."
    qubits = dict()
    qubit_count = 0
    stabilizers = []
    width = 4 * ((d - 1) // 2)
    for i in range(d - 1):
        for j in range(i + 1):
            center_x = 0.5 + 2 * j
            center_y = 1.5 + 2 * i
            if (i + j) % 2 == 0: # hexagon
                qs = [
                    (center_x - 0.5, center_y - 1.5),
                    (center_x - 0.5, center_y + 1.5),
                    (center_x + 0.5, center_y - 1.5),
                    (center_x + 0.5, center_y + 1.5),
                    (center_x - 1.5, center_y - 0.5),
                    (center_x - 1.5, center_y + 0.5),
                    (center_x + 1.5, center_y - 0.5),
                    (center_x + 1.5, center_y + 0.5),
                ]
            else:
                qs = [
                    (center_x - 0.5, center_y - 0.5),
                    (center_x - 0.5, center_y + 0.5),
                    (center_x + 0.5, center_y - 0.5),
                    (center_x + 0.5, center_y + 0.5),
                ]

            for q in qs:
                if q not in qubits and q[0] >= 0 and q[1] >= 0 and q[0] <= q[1] and q[1] <= width:
                    qubits[q] = qubit_count
                    qubit_count += 1   

    for i in range(d - 1):
        for j in range(i + 1):
            center_x = 0.5 + 2 * j
            center_y = 1.5 + 2 * i
            if (i + j) % 2 == 0: # hexagon
                qs = [
                    (center_x - 0.5, center_y - 1.5),
                    (center_x - 0.5, center_y + 1.5),
                    (center_x + 0.5, center_y - 1.5),
                    (center_x + 0.5, center_y + 1.5),
                    (center_x - 1.5, center_y - 0.5),
                    (center_x - 1.5, center_y + 0.5),
                    (center_x + 1.5, center_y - 0.5),
                    (center_x + 1.5, center_y + 0.5),
                ]
            else:
                qs = [
                    (center_x - 0.5, center_y - 0.5),
                    (center_x - 0.5, center_y + 0.5),
                    (center_x + 0.5, center_y - 0.5),
                    (center_x + 0.5, center_y + 0.5),
                ]
            
            pauli_x = ['I'] * qubit_count
            pauli_z = ['I'] * qubit_count
            for q in qs:
                if q in qubits:
                    pauli_x[qubits[q]] = 'X'
                    pauli_z[qubits[q]] = 'Z'
            
            stabilizers.append(''.join(pauli_x))
            stabilizers.append(''.join(pauli_z))

    return stabilizers

if __name__ == "__main__":
    d = 7
    stabilizers = generate_triangle_color_code(d)
    print(f'Num stabilizers: {len(stabilizers)}')
    for stab in stabilizers:
        print(f"\"{stab}\",")