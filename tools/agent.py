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
from circuit_metric import is_strictly_more_optimal, compute_metrics

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

def _resolve_model_and_provider(model: str) -> tuple[str, dict | None]:
    if model.startswith("ollama"):
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        if model in {"ollama", "ollama:", "ollama/"}:
            resolved_model = os.getenv("OLLAMA_MODEL", "ministral-3:8b")
        elif model.startswith("ollama:"):
            resolved_model = model.split(":", 1)[1].strip()
        else:
            resolved_model = model.split("/", 1)[1].strip()

        provider = {
            "type": "openai",
            "base_url": f"{base_url}/v1",
        }
        return resolved_model, provider

    return model, None

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
            resolved_model, provider = _resolve_model_and_provider(model)
            session_config = {
                "model": resolved_model,
                "tools": tools,
                "system_message": {
                    "content": system_message,
                },
            }
            if provider:
                session_config["provider"] = provider

            session = await client.create_session(session_config)

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

def generate_ft_state_prep(stabilizers: list[str], non_ft_circuit: str, 
    distance: int, qubits: list[int], attempts: int = 1, timeout: int | None = 60) -> stim.Circuit | None:
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
    # @define_tool(description="Return the final circuit as a string")
    # def return_result(params: CircuitParam) -> str:
    #     nonlocal result
    #     result = {
    #         "circuit": params.circuit,
    #         "data_qubits": params.data_qubits,
    #         "flag_qubits": params.flag_qubits
    #     }

    #     return "Result received. Stop generation."

    @define_tool(description=(
        "Submit the final fault-tolerant Stim circuit.\n"
        "Input must contain a single field 'stim_circuit' with raw Stim text.\n"
        "No markdown, no commentary."
    ))
    def return_result(params: FinalCircuitParam) -> str:
        nonlocal result
        try:
            parsed = stim.Circuit(params.stim_circuit)
        except Exception as e:
            return f"Failed to parse Stim circuit ({e}). Retry."

        result = {
            "circuit": params.stim_circuit
        }
        return "Final circuit received. Stop generation."

    
    prompt = f"""
    You are a quantum error correction assistant.
    Consider the following inputs and do not proceed unless all are provided:
        A quantum circuit {non_ft_circuit} described in Stim format, which prepares a state that is not necessarily fault-tolerant.
        The data qubits in the circuit {qubits}
        The distance of the code being prepared {distance}
        The circuit stabilizers {stabilizers_str}
    Once all inputs are provided, convert the given Stim circuit into a fault-tolerant version of the same circuit,
    using the following definition of fault tolerance (based on https://arxiv.org/pdf/quant-ph/0504218):
    Fault-tolerant requirements:
        Faults must not propagate beyond the qubit they are attached to (error weight must not exceed 1).
        Each ancilla qubit may interact with only one qubit in the data block.
        Measuring ancilla qubits in the X basis must yield an overall parity of 0.
    Transformation guidelines:
        Do not change the structure of the original circuit. You may add ancillas, but do not reorder gates on the original data qubits. 
        Introduce additional ancilla qubits if necessary to prevent multi-qubit error propagation.
        Ensure all ancilla-data interactions are strictly one-to-one.
        Preserve the logical action of the original circuit on the data qubits.
        Explicitly include X-basis measurements of ancilla qubits and enforce even parity.
        Ensure that the final circuit preserves the original stabilizers of the code.
    Output format requirements:
        Output only the final fault-tolerant Stim circuit.
        The output must be a plain string, for example:
        \"CX 0 3
        MX 3\"
    Do not include explanations, comments, validation notes, or analysis—only the fault-tolerant Stim circuit string."""

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



class OptimizeParam(BaseModel):
    candidate: str = Field(description="Candidate Stim circuit")
    baseline: str = Field(description="Baseline Stim circuit")


def generate_optimized_circuit(
    stabilizers: list[str],
    initial_circuit: str,
    *,
    model: str,
    attempts: int = 5,
    timeout: int | None = 600,
) -> stim.Circuit | None:
    """
    Optimize an existing Clifford circuit while preserving stabilizers.
    Uses lexicographic rule: (cx_count, volume, depth).
    """

    stabilizers_str = ", ".join(stabilizers)
    baseline_metrics = compute_metrics(initial_circuit).as_dict()

    agent_files_dir = os.path.join("data", model, "agent_files")
    os.makedirs(agent_files_dir, exist_ok=True)

    result = None

    @define_tool(description=(
        "Check whether a candidate circuit preserves all stabilizers.\n"
        "Returns dictionary of stabilizer -> bool and counts."
    ))
    def check_stabilizers_tool(params: CheckStabilizersParam) -> dict:
        try:
            _ = stim.Circuit(params.circuit)
        except Exception as e:
            return {"error": f"Failed to parse circuit: {e}"}

        results = check_stabilizers(params.circuit, params.stabilizers)
        preserved = sum(1 for v in results.values() if v)

        print("".join(['.' if v else '!' for v in results.values()]))

        return {
            "results": results,
            "preserved": preserved,
            "total": len(results)
        }

    @define_tool(description=(
    "Compare candidate circuit to baseline using lexicographic "
    "optimization rule (cx_count, volume, depth)."
))
    def evaluate_optimization(params: OptimizeParam) -> dict:
        try:
            better, info = is_strictly_more_optimal(
                candidate_text=params.candidate,
                baseline_text=params.baseline,
            )

            cand = info["candidate"]
            base = info["baseline"]

            print(
                f"[OPT] CX: {cand['cx_count']} (base {base['cx_count']}), "
                f"VOL: {cand['volume']} (base {base['volume']}), "
                f"DEPTH: {cand['depth']} (base {base['depth']}) "
                f"{'✓' if better else '✗'}"
            )

            return info

        except Exception as e:
            return {"error": str(e)}
    @define_tool(description=(
        "Submit final optimized circuit.\n"
        "Must preserve stabilizers and be strictly more optimal."
    ))
    def final_circuit(params: FinalCircuitParam) -> str:
        nonlocal result

        try:
            parsed = stim.Circuit(params.stim_circuit)
        except Exception as e:
            return f"Failed to parse Stim circuit ({e}). Retry."

        # Enforce stabilizer preservation
        stab_results = check_stabilizers(params.stim_circuit, stabilizers)
        if not all(stab_results.values()):
            return "Circuit does not preserve all stabilizers. Retry."

        # Enforce strict optimization
        better, info = is_strictly_more_optimal(
            candidate_text=params.stim_circuit,
            baseline_text=initial_circuit,
        )

        if not better:
            cand = info["candidate"]
            base = info["baseline"]

            print(
                f"[FINAL REJECTED] "
                f"CX {cand['cx_count']} vs {base['cx_count']}, "
                f"VOL {cand['volume']} vs {base['volume']}, "
                f"DEPTH {cand['depth']} vs {base['depth']}"
            )

            return "Circuit is not strictly more optimal. Retry."

        result = parsed
        return "Final optimized circuit accepted. Stop generation."

    # -------------------------------------------------
    # Prompt Construction
    # -------------------------------------------------
    with open("rq3/optimizer_prompt.txt", "r") as f:
        prompt_template = f.read()

    prompt = prompt_template.format(
        stabilizers_str=stabilizers_str,
        initial_circuit=initial_circuit,
        cx_count=baseline_metrics["cx_count"],
        volume=baseline_metrics["volume"],
        depth=baseline_metrics["depth"],
        attempts=attempts,
    )

    print(prompt)

    prompt_agent(prompt, tools=[evaluate_optimization, check_stabilizers_tool, final_circuit], model=model, timeout=timeout)

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



def main_optimizer():
    # ---- Target stabilizers (same set you used above, or swap as needed) ----
    stabilizers = [
        "XZZXI",
        "IXZZX",
        "XIXZZ",
        "ZXIXZ",
    ]

    # ---- Pick the model + run settings ----
    model = "claude-opus-4.6"
    attempts = 10
    timeout = 6000

    # ---- Provide an initial/baseline circuit to optimize ----
    # Option A: generate a baseline circuit first (recommended for quick testing)
    baseline_circuit = generate_state_prep(
        stabilizers,
        model=model,
        attempts=attempts,
        timeout=timeout,
    )
    if baseline_circuit is None:
        print("Failed to generate baseline circuit; cannot optimize.")
        return

    initial_circuit_text = str(baseline_circuit)

    # Option B: if you already have a baseline circuit string, use it instead:
    # initial_circuit_text = """H 0
    # CX 0 1
    # ..."""

    # ---- Run optimizer ----
    optimized = generate_optimized_circuit(
        stabilizers=stabilizers,
        initial_circuit=initial_circuit_text,
        model=model,
        attempts=attempts,
        timeout=timeout,
    )

    if optimized is None:
        print("No strictly better circuit found.")
        print("Baseline metrics:", compute_metrics(initial_circuit_text).as_dict())
        return

    print("Optimized circuit metrics:", compute_metrics(str(optimized)).as_dict())
    print(optimized)
#%%
if __name__ == "__main__":
    # main()
    main_optimizer()
# %%
