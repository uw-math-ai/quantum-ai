"""
MCP Server for Quantum Circuit Verification Tools

This server exposes quantum circuit verification functions as MCP tools:
- check_error_propagation: Analyze how single-qubit Pauli faults propagate through a quantum circuit
- check_stabilizers: Verify if stabilizers are preserved by a quantum circuit
"""

import json
from fastmcp import FastMCP

from check_error_propagation import check_error_propagation
from check_stabilizers import check_stabilizers


# Create FastMCP server instance
mcp = FastMCP("quantum-verification-server")


@mcp.tool()
def check_error_propagation_tool(
    circuit: str,
    data_qubits: list[int],
    flag_qubits: list[int]
) -> str:
    """Analyze how single-qubit Pauli faults (X, Y, Z) propagate through a quantum circuit.
    
    This tool injects faults at each gate location and tracks their propagation to assess
    fault tolerance and error detection capabilities. Returns detailed information about
    fault propagation including which qubits are affected and error weights on data and flag qubits.
    
    Args:
        circuit: A quantum circuit in Stim circuit format (e.g., 'H 0\\nCX 0 1\\nCX 1 2')
        data_qubits: List of qubit indices considered as data qubits
        flag_qubits: List of qubit indices considered as flag qubits (for error detection)
    
    Returns:
        Formatted string with error propagation analysis results and raw JSON data
    """
    try:
        results = check_error_propagation(circuit, data_qubits, flag_qubits)
        return json.dumps(results)
    except Exception as e:
        return f"Error during error propagation analysis: {str(e)}"


@mcp.tool()
def check_stabilizers_tool(
    circuit: str,
    stabilizers: list[str]
) -> str:
    """Check if given stabilizers are preserved by a quantum circuit.
    
    Stabilizers are Pauli operators that commute with the state prepared by the circuit.
    This is useful for verifying that a circuit correctly prepares an intended quantum state
    (e.g., checking if a GHZ state preparation circuit preserves the expected stabilizers).
    
    Args:
        circuit: A quantum circuit in Stim circuit format (e.g., 'H 0\\nCX 0 1\\nCX 1 2')
        stabilizers: List of stabilizer strings using Pauli notation (e.g., ['XXXX', 'ZIZI']).
                    Use 'I' for identity, 'X' for Pauli-X, 'Y' for Pauli-Y, 'Z' for Pauli-Z.
                    Stabilizers will be padded with 'I' to match the circuit's qubit count.
    
    Returns:
        Formatted string with stabilizer check results and raw JSON data
    """
    try:
        results = check_stabilizers(circuit, stabilizers)
        return json.dumps(results)
    except Exception as e:
        return f"Error during stabilizer check: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")