import json
import stim
import os
from dotenv import load_dotenv

from openai import AzureOpenAI
from check_stabilizers import check_stabilizers
from check_error_propagation import check_error_propagation

# Load environment variables from .env file
load_dotenv()

# -------------------------
# CONFIG
# -------------------------

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
API_VERSION = os.getenv("API_VERSION")

# -------------------------
# TOOL IMPLEMENTATION
# -------------------------

def generate_stim_circuit(stim_circuit: str) -> dict:
    """
    Tool execution logic.
    Validates and returns the Stim circuit string.
    """
    # Validate Stim syntax (raises if invalid)
    stim.Circuit(stim_circuit)

    return {
        "stim_circuit": stim_circuit
    }


def return_final_circuit(circuit: str, stabilizers_preserved: bool, bad_faults: int, analysis: str) -> dict:
    """
    Return the final circuit output. Call this when you have the best circuit ready.
    
    Args:
        circuit: Stim circuit string
        stabilizers_preserved: Whether all stabilizers are preserved
        bad_faults: Number of bad faults (data_weight > 1 AND flag_weight < 1)
        analysis: Explanation of the design choices
        
    Returns:
        The complete output dictionary
    """
    return {
        "circuit": circuit,
        "stabilizers_preserved": stabilizers_preserved,
        "bad_faults": bad_faults,
        "analysis": analysis
    }


def generate_ft_state_prep(stabilizers: list[str], data_qubits: list[int] | None = None, attempts: int = 1) -> stim.Circuit:
    """
    Generate a fault-tolerant state preparation circuit for given stabilizers.
    
    Args:
        stabilizers: List of stabilizer strings (e.g., ['XXXX', 'ZIZI'])
        data_qubits: List of data qubit indices. If None, infers from first stabilizer length.
        attempts: Number of circuit design iterations to try. Returns the best one.
    
    Returns:
        stim.Circuit: The generated fault-tolerant circuit with minimum bad faults
    """
    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=API_VERSION
    )
    
    # Infer data qubits if not provided
    if data_qubits is None:
        num_data_qubits = len(stabilizers[0])
        data_qubits = list(range(num_data_qubits))
    
    # Format stabilizers for display
    stabilizers_str = ", ".join(stabilizers)
    
    # Define tools
    tools = [
        {
            "type": "function",
            "function": {
                "name": "generate_stim_circuit",
                "description": "Generate a quantum circuit in Stim format",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "stim_circuit": {
                            "type": "string",
                            "description": "Valid Stim circuit text"
                        }
                    },
                    "required": ["stim_circuit"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_stabilizers",
                "description": "Verify if a quantum circuit preserves the given stabilizers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "circuit": {
                            "type": "string",
                            "description": "Stim circuit text"
                        },
                        "stabilizers": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of stabilizer strings (e.g., ['XXXX', 'ZIZI'])"
                        }
                    },
                    "required": ["circuit", "stabilizers"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_error_propagation",
                "description": "Check how single-qubit Pauli faults propagate through a circuit",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "circuit": {
                            "type": "string",
                            "description": "Stim circuit text"
                        },
                        "data_qubits": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "List of data qubit indices"
                        },
                        "flag_qubits": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "List of flag qubit indices"
                        }
                    },
                    "required": ["circuit", "data_qubits", "flag_qubits"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "return_final_circuit",
                "description": "Return your final circuit result. Call this once you have selected the best circuit.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "circuit": {
                            "type": "string",
                            "description": "The Stim circuit string"
                        },
                        "stabilizers_preserved": {
                            "type": "boolean",
                            "description": "Whether all stabilizers are preserved (must be true)"
                        },
                        "bad_faults": {
                            "type": "integer",
                            "description": "Number of bad faults in the circuit"
                        },
                        "analysis": {
                            "type": "string",
                            "description": "Explanation of design choices and why this circuit was selected"
                        }
                    },
                    "required": ["circuit", "stabilizers_preserved", "bad_faults", "analysis"]
                }
            }
        }
    ]
    
    # Build messages
    messages = [
        {
            "role": "system",
            "content": f"""Generate fault-tolerant quantum state preparation circuits in Stim circuit string format.

Goals:
    (1) ALL stabilizers must be preserved. This is mandatory for a valid circuit.
    (2) minimize bad faults. A bad fault is defined by having data_weight > 1 and flag_weight < 1 as returned by check_error_propagation.

Approach: Design a Stim circuit on data qubits that preserves the stabilizers. Add flag qubits for error detection (measured, not affecting data qubit gates).

Constraints:
- Clifford gates only: H, S, S_DAG, CX, CY, CZ, X, Y, Z, SQRT_X, SQRT_Y (i.e., no RESET, no T gates, etc.)
- Measure only flags, never data qubits
- No comments (# lines)

Workflow: Design circuit -> check_stabilizers -> (if needed) check_error_propagation -> return_final_circuit"""
        },
        {
            "role": "user",
            "content": f"""Stabilizers: {stabilizers_str}
Data qubits: {data_qubits} (prepare state here, don't measure)
Flag qubits: [{len(data_qubits)}, {len(data_qubits) + 1},...] (for error detection)
Attempts: {attempts}

Create {attempts} circuit(s), verify stabilizers are preserved, and call return_final_circuit with a VALID circuit that minimizes bad faults."""
        }
    ]
    
    # First API call
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=tools,
        tool_choice="required"
    )
    
    # Handle tool calls
    response_message = response.choices[0].message
    final_result = None
    
    while response_message.tool_calls:
        messages.append(response_message)
        
        for tool_call in response_message.tool_calls:
            # Parse arguments
            args = json.loads(tool_call.function.arguments)
            
            # Execute tool based on name
            if tool_call.function.name == "generate_stim_circuit":
                result = generate_stim_circuit(
                    stim_circuit=args["stim_circuit"]
                )
            elif tool_call.function.name == "check_stabilizers":
                result = check_stabilizers(
                    circuit=args["circuit"],
                    stabilizers=args["stabilizers"]
                )
            elif tool_call.function.name == "check_error_propagation":
                result = check_error_propagation(
                    circuit=args["circuit"],
                    data_qubits=args["data_qubits"],
                    flag_qubits=args["flag_qubits"]
                )
            elif tool_call.function.name == "return_final_circuit":
                # This is the final result - capture it
                final_result = return_final_circuit(
                    circuit=args["circuit"],
                    stabilizers_preserved=args["stabilizers_preserved"],
                    bad_faults=args["bad_faults"],
                    analysis=args["analysis"]
                )
                result = {"status": "success", "message": "Circuit received"}
            else:
                result = {"error": f"Unknown tool: {tool_call.function.name}"}
            
            # Add tool response to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })
        
        # If we got the final result, break out of the loop
        if final_result:
            break
        
        # Get next response
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=tools
        )
        response_message = response.choices[0].message
        
        # Debug: check if model finished without calling return_final_circuit
        if not response_message.tool_calls and not final_result:
            print(f"Warning: Model finished without calling return_final_circuit")
            print(f"Final message: {response_message.content[:200] if response_message.content else 'No content'}")
    
    # Return the circuit from the final result
    if final_result:
        circuit_str = final_result.get("circuit", "")
        if not circuit_str:
            raise ValueError(f"No circuit in final result")
        return stim.Circuit(circuit_str)
    
    raise ValueError("No circuit generated - return_final_circuit was not called")


# -------------------------
# MAIN
# -------------------------

def main():
    """Demo: Generate fault-tolerant circuits for different stabilizers."""
    
    # Example 1: 4-qubit GHZ state with XXXX and ZZII, IZZI stabilizers
    print("="*80)
    print("Example 1: 4-qubit GHZ state (XXXX, ZZII, IZZI) - 3 attempts")
    print("="*80)
    stabilizers1 = ['XXXX', 'ZZII', 'IZZI']
    data_qubits1 = [0, 1, 2, 3]
    
    circuit1 = generate_ft_state_prep(stabilizers1, data_qubits1, attempts=3)
    print("\nBest Circuit:")
    print(circuit1)
    print("\nCircuit Diagram:")
    print(circuit1.diagram())
    
    # Find flag qubits
    all_qubits1 = set(range(circuit1.num_qubits))
    flag_qubits1 = list(all_qubits1 - set(data_qubits1))
    print(f"\nData qubits: {data_qubits1}")
    print(f"Flag qubits: {flag_qubits1}")
    
    # Verify stabilizers
    print("\nStabilizer verification:")
    stab_results1 = check_stabilizers(str(circuit1), stabilizers1)
    for stab, preserved in stab_results1.items():
        status = "✓" if preserved else "✗"
        print(f"  {status} {stab}: {preserved}")
    
    # Check error propagation
    print("\nError propagation analysis:")
    error_results1 = check_error_propagation(str(circuit1), data_qubits1, flag_qubits1)
    bad_faults1 = [r for r in error_results1 if r['data_weight'] > 1 and r['flag_weight'] < 1]
    print(f"  Total faults analyzed: {len(error_results1)}")
    print(f"  Bad faults: {len(bad_faults1)}")
    if len(bad_faults1) == 0:
        print("  ✓ Circuit is fault-tolerant!")
    else:
        print(f"  ✗ Circuit has {len(bad_faults1)} undetected multi-qubit errors")
    
    print("\n")
    
    # Example 2: [[3,1]] stabilizer code with complete stabilizer set
    # print("="*80)
    # print("Example 2: [[3,1]] code (XXX, ZZI) - 3 attempts")
    # print("="*80)
    # stabilizers2 = ['XXX', 'ZZI']
    # data_qubits2 = [0, 1, 2]
    
    # circuit2 = generate_ft_state_prep(stabilizers2, data_qubits2, attempts=3)
    # print("\nBest Circuit:")
    # print(circuit2)
    # print("\nCircuit Diagram:")
    # print(circuit2.diagram())
    
    # # Find flag qubits
    # all_qubits2 = set(range(circuit2.num_qubits))
    # flag_qubits2 = list(all_qubits2 - set(data_qubits2))
    # print(f"\nData qubits: {data_qubits2}")
    # print(f"Flag qubits: {flag_qubits2}")
    
    # # Verify stabilizers
    # print("\nStabilizer verification:")
    # stab_results2 = check_stabilizers(str(circuit2), stabilizers2)
    # for stab, preserved in stab_results2.items():
    #     status = "✓" if preserved else "✗"
    #     print(f"  {status} {stab}: {preserved}")
    
    # # Check error propagation
    # print("\nError propagation analysis:")
    # error_results2 = check_error_propagation(str(circuit2), data_qubits2, flag_qubits2)
    # bad_faults2 = [r for r in error_results2 if r['data_weight'] > 1 and r['flag_weight'] < 1]
    # print(f"  Total faults analyzed: {len(error_results2)}")
    # print(f"  Bad faults: {len(bad_faults2)}")
    # if len(bad_faults2) == 0:
    #     print("  ✓ Circuit is fault-tolerant!")
    # else:
    #     print(f"  ✗ Circuit has {len(bad_faults2)} undetected multi-qubit errors")
    
    # print("\n")


if __name__ == "__main__":
    main()