import stim
import asyncio
from dotenv import load_dotenv
from copilot.types import Tool, Attachment
from copilot.tools import define_tool
from copilot import CopilotClient
from copilot.generated.session_events import SessionEventType
from pydantic import BaseModel, Field

from check_stabilizers import check_stabilizers
from check_error_propagation import check_fault_tolerance

load_dotenv()

class CircuitParam(BaseModel):
    circuit: str = Field(description="The Stim circuit description as a string")
    stabilizers: list[str] = Field(description="List of stabilizer strings")
    data_qubits: list[int] = Field(description="List of data qubit indices")
    flag_qubits: list[int] = Field(description="List of flag qubit indices")

@define_tool(description="""Validate correctness and fault-tolerance of a Stim circuit.
             Checks stabilizer preservation, error propagation, and fault-tolerance
             Returns a dictionary with which stabilizers are preserved, error propagation results, and fault-tolerance status""")
def validate_circuit(circuit: CircuitParam) -> dict:
    try:
        _ = stim.Circuit(circuit.circuit)
    except Exception as e:
        return {"error": f"Failed to parse circuit: {e}"}

    stab_results = check_stabilizers(circuit.circuit, circuit.stabilizers)
    error_propagation_results, fault_tolerance_results = check_fault_tolerance(circuit.circuit, circuit.data_qubits, circuit.flag_qubits)

    return {
        "stabilizers": stab_results,
        "error_propagation": error_propagation_results,
        "fault_tolerance": fault_tolerance_results
    }

def prompt_agent(prompt: str, system_message: str = "", tools: list[Tool] | None = None, model: str = "gpt-4.1",
                 attachments: list[Attachment | dict] | None = None, timeout: int | None = 60) -> str:
    """Prompt the Copilot agent and return the response."""
    if tools is None:
        tools = []
    if attachments is None:
        attachments = []

    async def run():
        client = CopilotClient({"auto_start": True})
        try:
            session = await client.create_session({
                "model": model,
                "tools": tools,
                "system_message": {
                    "content": system_message,
                }
            })

            response = ""

            def handle_event(event):
                nonlocal response
                if event.type == SessionEventType.ASSISTANT_MESSAGE:
                    response = event.data.content or ""

            session.on(handle_event)

            await session.send_and_wait({"prompt": prompt, "attachments": attachments}, timeout=timeout)

            return response
        finally:
            await client.stop()

    return asyncio.run(run())


# NOTE: this is a proof-of-concept implementation for End-to-End generation. May need individual function for RQ1, RQ2, RQ3
def generate_ft_state_prep(stabilizers: list[str], attempts: int = 1, timeout: int | None = 60) -> stim.Circuit | None:
    """
    Generate a fault-tolerant state preparation circuit for given stabilizers.
    
    Args:
        stabilizers: List of stabilizer strings (e.g., ['XXXX', 'ZIZI'])
        attempts: Number of circuit design iterations to try. Returns the best one.
    
    Returns:
        stim.Circuit: The generated fault-tolerant circuit with minimum bad faults or None if generation failed.
    """
    
    # Format stabilizers for display
    stabilizers_str = ", ".join(stabilizers)

    result = {}
    @define_tool(description="Return the final circuit as a string")
    def return_result(params: CircuitParam) -> str:
        nonlocal result
        result = {
            "circuit": params.circuit,
            "data_qubits": params.data_qubits,
            "flag_qubits": params.flag_qubits
        }

        return "Result received. Stop generation."
    
    prompt = f"""Generate a fault-tolerant Stim circuit to prepare the stabilizer state defined by the following stabilizers: {stabilizers_str}.
    Use flag qubits as needed to ensure fault-tolerance.
    Always verify the correctness and fault-tolerance of the circuit using the validate_circuit tool. Retry if any stabilizers are not preserved or if the circuit is not fault-tolerant.
    You have {attempts} attempts to generate the best possible circuit.
    Call the return_result tool before ending with the best iteration."""

    prompt_agent(prompt, tools=[validate_circuit, return_result], timeout=timeout)

    # Check if result was populated by the agent
    if not result or "circuit" not in result:
        return None

    return stim.Circuit(result["circuit"])


# -------------------------
# MAIN
# -------------------------

def main():
    circ = generate_ft_state_prep(['XXXX', 'ZZII', 'IZZI'], attempts=1, timeout=300)
    print(circ.diagram() if circ else "No circuit generated.")
    
    print(prompt_agent("Please read the attachment and give a response.", attachments=[{"type":"file", "path":"./tools/test-attachment.txt"}]))

if __name__ == "__main__":
    main()