def get_baseline():
    return """H 0 1 3
CX 0 1 0 3 0 6 0 8 6 1 1 6 6 1 1 5
H 2
CX 2 5 3 4 6 4 4 6 6 4 4 5 4 6 4 8 7 6 8 6 8 7"""

def generate_circuit():
    circuit = get_baseline()
    ops = []

    # Ancillas 9-16
    # Stabilizers
    # 0: XXIXXIIII (0,1,3,4) X -> 9
    # 1: IIIIXXIXX (4,5,7,8) X -> 10
    # 2: IIXIIXIII (2,5,8) X -> 11
    # 3: IIIXIIXII (3,6,8) X -> 12
    # 4: IIIZZIZZI (3,4,6,7) Z -> 13
    # 5: IZZIZZIII (1,2,4,5) Z -> 14
    # 6: ZZIIIIIII (0,1) Z -> 15
    # 7: IIIIIIIZZ (7,8) Z -> 16

    # X checks (9,10,11,12) - need H before and after
    ops.append("H 9 10 11 12")

    # CX control ancilla, target data for X checks
    ops.append("CX 9 0 9 1 9 3 9 4")
    ops.append("CX 10 4 10 5 10 7 10 8")
    ops.append("CX 11 2 11 5 11 8")
    ops.append("CX 12 3 12 6 12 8")

    ops.append("H 9 10 11 12")

    # Z checks (13,14,15,16) - CX control data, target ancilla
    ops.append("CX 3 13 4 13 6 13 7 13")
    ops.append("CX 1 14 2 14 4 14 5 14")
    ops.append("CX 0 15 1 15")
    ops.append("CX 7 16 8 16")

    # Measure ancillas
    ops.append("M 9 10 11 12 13 14 15 16")

    return circuit + "\n" + "\n".join(ops)

if __name__ == "__main__":
    print(generate_circuit())
