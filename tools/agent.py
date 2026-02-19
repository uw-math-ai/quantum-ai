#%%
import os
import stim
import asyncio
from dotenv import load_dotenv
from copilot.types import Tool, Attachment
from copilot.tools import define_tool
from copilot import CopilotClient
from copilot.generated.session_events import SessionEventType, SessionEvent
from pydantic import BaseModel, Field

from check_stabilizers import check_stabilizers
from check_error_propagation import check_fault_tolerance

load_dotenv()

class CircuitParam(BaseModel):
    circuit: str = Field(description="The Stim circuit description as a string")
    stabilizers: list[str] = Field(description="List of stabilizer strings")
    data_qubits: list[int] = Field(description="List of data qubit indices")
    flag_qubits: list[int] = Field(description="List of flag qubit indices")


class CheckStabilizersParam(BaseModel):
    circuit: str = Field(description="The Stim circuit description as a string")
    stabilizers: list[str] = Field(description="List of stabilizer strings (e.g. ['XXXX', 'ZIZI'])")


class FinalCircuitParam(BaseModel):
    stim_circuit: str = Field(
        description=(
            "Raw Stim circuit text to be treated as the FINAL answer. "
            "Provide only the circuit body (no Markdown fences, no prose, no ---OUTPUT--- markers). "
            "The text must be parseable by stim.Circuit." 
        )
    )

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

            def handle_event(event: SessionEvent):
                nonlocal response
                if event.type == SessionEventType.ASSISTANT_MESSAGE:
                    if event.data.content:
                        print(event.data.content)
                    response = event.data.content or ""

            session.on(handle_event)

            await session.send_and_wait({"prompt": prompt, "attachments": attachments}, timeout=timeout)

            return response
        finally:
            await client.stop()

    return asyncio.run(run())

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
    
    prompt = f"""
Generate a fault-tolerant Stim circuit to prepare the stabilizer state defined by the following stabilizers: {stabilizers_str}.
Use flag qubits as needed to ensure fault-tolerance.
Always verify the correctness and fault-tolerance of the circuit using the validate_circuit tool. Retry if any stabilizers are not preserved or if the circuit is not fault-tolerant.
You have {attempts} attempts to generate the best possible circuit.
Dont' try to write or evaluate any code in the repo, just print the stim circuit between "---OUTPUT---" marks.

Call the return_result tool before ending with the best iteration."""

    prompt_agent(prompt, tools=[validate_circuit, return_result], timeout=timeout)

    # Check if result was populated by the agent
    if not result or "circuit" not in result:
        return None

    return stim.Circuit(result["circuit"])

def generate_state_prep(stabilizers: list[str], *, model:str, attempts: int = 1, timeout: int | None = 600) -> stim.Circuit | None:
    """
    Generate a state preparation circuit for given stabilizers (without fault-tolerance requirement).
    
    Args:
        stabilizers: List of stabilizer strings (e.g., ['XXXX', 'ZIZI'])
        attempts: Number of circuit design iterations to try. Returns the best one.
    
    Returns:
        stim.Circuit: The generated circuit or None if generation failed.
    """
    
    # Format stabilizers for display
    stabilizers_str = ", ".join(stabilizers)
    qubits_count = len(stabilizers[0])

    # Create a scratch directory for any temporary files the agent may write
    agent_files_dir = os.path.join("data", model, "agent_files")
    os.makedirs(agent_files_dir, exist_ok=True)

    result = None
    @define_tool(description=(
        "Submit the final, best Stim circuit back to the harness.\n\n"
        "Input: a single field 'stim_circuit' containing the raw Stim circuit text.\n"
        "Constraints: must be valid Stim format; do not wrap in Markdown code fences; no extra commentary.\n\n"
        "Example input:\n"
        "{\n"
        "  \"stim_circuit\": \"H 0\\nCX 0 1\\nM 0 1\"\n"
        "}"
    ))
    def final_circuit(params: FinalCircuitParam) -> str:
        nonlocal result
        try:
            parsed = stim.Circuit(params.stim_circuit)
        except Exception as e:
            return f"Failed to parse Stim circuit ({e}). Please retry with valid Stim circuit text only."

        result = parsed
        return "Final circuit received. Stop generation."    

    @define_tool(description=(
        "Evaluate a candidate Stim circuit against the target stabilizers.\n\n"
        "Input: { 'circuit': <stim text>, 'stabilizers': [<stabilizer strings>] }\n\n"
        "Return value (on success):\n"
        "{\n"
        "  'results': {<stabilizer>: <bool>, ...},\n"
        "  'preserved': <int>,\n"
        "  'total': <int>\n"
        "}\n"
        "Return value (on failure): { 'error': <string> }"
    ))
    def check_stabilizers_tool(params: CheckStabilizersParam) -> dict:
        try:
            _ = stim.Circuit(params.circuit)
        except Exception as e:
            return {"error": f"Failed to parse circuit: {e}"}

        result = check_stabilizers(params.circuit, params.stabilizers)
        print("".join(['.' if s else '!' for s in result.values()]))
        preserved = sum(1 for ok in result.values() if ok)
        return {"results": result, "preserved": preserved, "total": len(result)}

    
    with open("rq1/prompt.txt", "r") as f:
        prompt_template = f.read()

    prompt = prompt_template.format(
        stabilizers_str=stabilizers_str,
        qubits_count=qubits_count,
        qubits_count_less_1=qubits_count - 1,
        attempts=attempts,
        agent_files_dir=agent_files_dir
    )

    print(prompt)

    prompt_agent(prompt, tools=[check_stabilizers_tool, final_circuit], model=model, timeout=timeout)

    # Check if result was populated by the agent
    if not result:
        return None

    print('done.')
    return result

# -------------------------
# MAIN
# -------------------------

def main():
    # circ = generate_ft_state_prep(['XXXX', 'ZZII', 'IZZI'], attempts=1, timeout=300)
    # print(circ.diagram() if circ else "No circuit generated.")
    
    # print(prompt_agent("Please read the attachment and give a response.", attachments=[{"type":"file", "path":"./tools/test-attachment.txt"}]))
    stabilizers = [
        "XZZXI",
        "IXZZX",
        "XIXZZ",
        "ZXIXZ"
        ]
    model = "claude-opus-4.6"
    # model = "claude-sonnet-4.5"
    # model = "gemini-3-pro-preview"
    # model = "gpt-5.2"
    attempts = 10
    result = generate_state_prep(stabilizers, model=model, attempts=attempts, timeout=6000)
    print(result)

#%%
if __name__ == "__main__":
    main()
# %%
