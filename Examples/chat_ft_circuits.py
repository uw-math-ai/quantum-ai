import stim
from ft_example_circuits import visualize


# circuit = """
#         H 0
#         CX 0 1
#         CX 1 2
#         CX 2 3
#     """
def simple_circuit_1():
    circuit = """
        H 0
        CX 0 1
        CX 1 2
        CX 2 3
        CX 0 4
        CX 1 4
        CX 1 5
        M 4
        M 5
        CX 1 4
        CX 2 4
        CX 2 5
        M 4 
        M 5
        CX 2 4
        CX 3 4
        CX 3 5
        M 4
        M 5
    """
    return str(circuit)

circuit = simple_circuit_1()
visualize(circuit)