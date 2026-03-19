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
from pathlib import Path
import json


from check_stabilizers import check_stabilizers
from check_error_propagation import check_fault_tolerance, ft_score
from circuit_metric import is_strictly_more_optimal, compute_metrics

load_dotenv()

class CircuitParam(BaseModel):
    circuit: str = Field(description="The Stim circuit description as a string")
    stabilizers: list[str] = Field(description="List of stabilizer strings")
    data_qubits: list[int] = Field(description="List of data qubit indices")
    flag_qubits: list[int] = Field(description="List of flag qubit indices")


class CheckStabilizersParam(BaseModel):
    circuit: str = Field(description="The Stim circuit description as a string")


class FinalCircuitParam(BaseModel):
    stim_circuit: str = Field(
        description=(
            "Raw Stim circuit text to be treated as the FINAL answer. "
            "Provide only the circuit body (no Markdown fences, no prose, no ---OUTPUT--- markers). "
            "The text must be parseable by stim.Circuit." 
        )
    )

class FTResultParam(BaseModel):
    stim_circuit: str = Field(
        description="Raw Stim circuit text (no markdown, no commentary)."
    )
    ancilla_qubits: list[int] = Field(
        description="List of newly introduced ancilla qubit indices."
    )



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
    distance: int, attempts: int | None = 3, timeout: int | None = 60, *, model: str,
    prompt_file: str = "rq2/prompts/ft_state_prep_prompt.txt") -> tuple[stim.Circuit, list[dict]] | None:
    """
    Generate a fault-tolerant state preparation circuit for given stabilizers.
    
    Args:
        stabilizers: List of stabilizer strings (e.g., ['XXXX', 'ZIZI'])
        attempts: Number of circuit design iterations to try. Returns the best one.
    
    Returns:
        stim.Circuit: The generated fault-tolerant circuit with minimum bad faults or None if generation failed.
    """
    # Track all intermediate circuits
    all_candidates = []

    # Format stabilizers for display
    stabilizers_str = ", ".join(stabilizers)

    # Create a scratch directory for any temporary files the agent may write
    agent_files_dir = os.path.join("data", model, "agent_files_ft")
    os.makedirs(agent_files_dir, exist_ok=True)

    result = None

    @define_tool(description=(
        "Submit the final fault-tolerant circuit and its ancilla qubits.\n"
        "Fields:\n"
        "- stim_circuit: raw Stim circuit text\n"
        "- ancilla_qubits: list of integers\n"
        "Do not include markdown or commentary."
    ))
    def return_result(params: FTResultParam) -> str:
        nonlocal result
        try:
            parsed = stim.Circuit(params.stim_circuit)
        except Exception as e:
            return f"Failed to parse Stim circuit ({e}). Retry."

        result = {"circuit": parsed}
        return "Final circuit received. Stop generation."

    
    @define_tool(description="""Validate correctness and fault-tolerance of a Stim circuit.

        This tool evaluates a candidate circuit produced by the agent.

        Checks performed:
        1. Stabilizer Preservation
            Verifies that the circuit preserves the provided stabilizer generators.

        2. Error Propagation Analysis
            Injects single-qubit Pauli faults (X, Y, Z) at each gate location and propagates
            them through the remainder of the circuit to determine how errors spread.

        3. Fault-Tolerance Check
            Determines whether the circuit satisfies the fault-tolerance condition:
            - Any fault propagating to more than floor((distance - 1)/2) data qubits
                must trigger a flag ancilla (X error on a flag qubit).

        4. Fault-Tolerance Score
            Computes a continuous score that penalizes undetected high-weight faults.

        Returns a dictionary containing:
        - Whether the circuit is fault tolerant
        - How many stabilizers are preserved
        - The fault tolerance score
        - The most severe error propagation events""") 
    def validate_circuit(circuit: CircuitParam) -> dict:
        try:
            parsed = stim.Circuit(circuit.circuit)
        except Exception as e:
            return {"error": f"Failed to parse circuit: {e}"}

        ancillas = compute_ancillas(parsed, circuit.data_qubits)

        # check stabilizers
        result = check_stabilizers(circuit.circuit, circuit.stabilizers)
        print("".join(['.' if s else '!' for s in result.values()]))
        preserved = sum(1 for ok in result.values() if ok)
        all_stabilized = all(result.values())

        # check error propagation and fault tolerance
        error_propagation_results, fault_tolerance_results = check_fault_tolerance(circuit.circuit, circuit.data_qubits, ancillas, distance)        

        # Sort propagation results by highest data weight (worst faults)
        sorted_errors = sorted(
            error_propagation_results,
            key=lambda r: r["data_weight"],
            reverse=True
        )

        # Return only the worst 10 faults
        top_errors = sorted_errors[:10]

        # find the ft score
        score = ft_score(circuit.circuit, circuit.data_qubits, ancillas, distance)
        

        # Append candidate to list
        all_candidates.append({
            "circuit": str(parsed),
            "ft_score": score,
            "all_stabilized": all_stabilized,
            "preserved_stabilizers": preserved,
        })

        print(f"attempt:{len(all_candidates)}, score:{score}, stabilizers:{preserved}")

        return {
            "fault_tolerance": fault_tolerance_results,
            "error_propagation": top_errors, 
            "preserved_stabilizers": preserved,
            "ft_score": score
        } 

    def compute_ancillas(parsed_circuit, data_qubits):
        used_qubits = set()
        for inst in parsed_circuit:
            for t in inst.targets_copy():
                if hasattr(t, "value"):
                    used_qubits.add(t.value)
        return sorted(list(used_qubits - set(data_qubits)))

    with open(prompt_file, "r") as f:
        prompt_template = f.read()

    prompt = prompt_template.format(
        non_ft_circuit=non_ft_circuit,
        distance=distance,
        stabilizers_str=stabilizers_str,
        agent_files_dir=agent_files_dir,
        attempts=attempts,
    )

    print(prompt)

    try:
        prompt_agent(prompt, tools=[validate_circuit, return_result], model=model, timeout=timeout)
    except Exception as e:
        print(f"  ⚠ generate_ft_state_prep caught exception: {e}")

    if result is None:
        return None, all_candidates

    return result, all_candidates


def generate_state_prep(stabilizers: list[str], *, model:str, attempts: int = 1, timeout: int | None = 600, prompt_file: str = "rq1/prompts/state_prep_prompt4.txt") -> stim.Circuit | None:
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

        result = check_stabilizers(params.circuit, stabilizers)
        print("".join(['.' if s else '!' for s in result.values()]))
        preserved = sum(1 for ok in result.values() if ok)
        return {"results": result, "preserved": preserved, "total": len(result)}

    
    with open(prompt_file, "r") as f:
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


def generate_optimized_circuit(
    stabilizers: list[str],
    initial_circuit: str,
    *,
    prompt_template: str,
    model: str,
    attempts: int = 10,
    timeout: int | None = 6000,
) -> dict:
    """
    Optimize an existing Clifford circuit while preserving stabilizers.
    Uses lexicographic rule: (cx_count, volume, depth).

    Args:
        stabilizers: List of stabilizer strings.
        initial_circuit: Baseline Stim circuit text to optimize.
        prompt_template: A format-string prompt with placeholders
            {stabilizers_str}, {initial_circuit}, {attempts}, {agent_files_dir}.
        model: LLM model identifier.
        attempts: Number of optimization attempts.
        timeout: Timeout in seconds.

    Returns:
        dict with keys:
            'circuit': stim.Circuit | None  – the accepted optimized circuit, or None if none accepted.
            'evaluations': list[dict]       – intermediate results from each evaluate_optimization call,
                each containing 'circuit', 'preserved_stabilizers', 'candidate', 'baseline', 'better'.
    """

    stabilizers_str = ", ".join(stabilizers)
    baseline_metrics = compute_metrics(initial_circuit).as_dict()

    repo_root = Path(__file__).resolve().parents[1] 
    agent_files_dir = repo_root / "rq3" / "data" / model / "agent_files"
    agent_files_dir.mkdir(parents=True, exist_ok=True)

    result = None
    evaluations = []

    @define_tool(description=(
        "Evaluate a candidate Stim circuit for correctness AND optimization.\n\n"
        "This is the primary evaluation tool. It performs two checks in order:\n\n"
        "1. STABILIZER PRESERVATION – simulates the circuit with a TableauSimulator\n"
        "   to verify that every target stabilizer has expectation +1. If any\n"
        "   stabilizer is not preserved the circuit is INVALID and cannot be\n"
        "   submitted via final_circuit.\n\n"
        "2. OPTIMIZATION COMPARISON – compares the candidate against the baseline\n"
        "   using a strict lexicographic rule on three integer metrics:\n"
        "     a. cx_count  – number of CX (CNOT) gates (primary, most important).\n"
        "     b. volume    – total gate count in the volume gate set\n"
        "                    (CX, CY, CZ, H, S, SQRT_X, etc.).\n"
        "   A candidate is 'strictly better' only when the tuple\n"
        "   (cand.cx_count, cand.volume) is lexicographically less than\n"
        "   the baseline tuple. Equal tuples are NOT an improvement.\n\n"
        "Input:\n"
        "  - candidate: raw Stim circuit text (no Markdown fences). Must be\n"
        "    parseable by stim.Circuit.\n\n"
        "Output (on success):\n"
        "  {\n"
        "    'preserved_stabilizers': <int>  (number of stabilizers preserved out of total),\n"
        "    'valid': true/false             (true when ALL stabilizers are preserved),\n"
        "    'candidate': { 'cx_count': int, 'volume': int, 'depth': int, ... },\n"
        "    'baseline':  { 'cx_count': int, 'volume': int, 'depth': int, ... },\n"
        "    'better': true/false\n"
        "  }\n\n"
        "Output (on parse / error): { 'error': <string> }\n\n"
        "Usage guidance:\n"
        "  - Call this tool to check every candidate circuit before submitting\n"
        "    via final_circuit.\n"
        "  - A circuit must have valid == true AND better == true to be\n"
        "    accepted by final_circuit.\n"
        "  - Focus optimization efforts on reducing cx_count first; only then\n"
        "    try to reduce volume or depth."
    ))
    def evaluate_optimization(params: OptimizeParam) -> dict:
        try:
            parsed = stim.Circuit(params.candidate)
        except Exception as e:
            return {"error": f"Failed to parse circuit: {e}"}

        # --- stabilizer check ---
        stab_results = check_stabilizers(params.candidate, stabilizers)
        preserved = sum(1 for v in stab_results.values() if v)
        all_preserved = preserved == len(stab_results)

        print("".join(['.' if v else '!' for v in stab_results.values()]))

        # --- optimization comparison ---
        better, info = is_strictly_more_optimal(
            candidate_text=params.candidate,
            baseline_text=initial_circuit,
        )

        cand = info["candidate"]
        base = info["baseline"]

        print(
            f"[OPT] CX: {cand['cx_count']} (base {base['cx_count']}), "
            f"VOL: {cand['volume']} (base {base['volume']}), "
            f"DEPTH: {cand['depth']} (base {base['depth']}) "
            f"{'✓' if better else '✗'} | "
            f"stabilizers: {preserved}/{len(stab_results)} "
            f"{'✓' if all_preserved else '✗'}"
        )

        result = {
            "preserved_stabilizers": preserved,
            "valid": all_preserved,
            "candidate": cand,
            "baseline": base,
            "better": better,
        }

        # Track this evaluation for intermediate results
        evaluations.append({
            "circuit": params.candidate,
            **result,
        })

        return result
    

    @define_tool(description=(
        "Submit the final optimized Stim circuit for acceptance.\n\n"
        "This tool performs TWO automatic validation checks before accepting:\n"
        "  1. Stabilizer preservation – every target stabilizer must be satisfied.\n"
        "  2. Strict optimization     – the circuit must be lexicographically better \n"
        "     than the baseline on (cx_count, volume).\n\n"
        "If either check fails the submission is REJECTED and you should keep \n"
        "iterating. The tool returns a message indicating success or failure.\n\n"
        "Input:\n"
        "  - stim_circuit: raw Stim circuit text (no Markdown fences, no prose).\n"
        "    Must be parseable by stim.Circuit.\n\n"
        "Output:\n"
        "  - On success: 'Final optimized circuit accepted. Stop generation.'\n"
        "  - On failure: a description of what went wrong (stabilizers or metrics).\n\n"
        "Best practice:\n"
        "  - Always call evaluate_optimization first to verify that\n"
        "    valid == true AND better == true before submitting here.\n"
        "  - Only call this tool with your final answer."
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

            return "Circuit is NOT strictly more optimal."

        result = parsed
        return "Final optimized circuit accepted."

    # -------------------------------------------------
    # Prompt Construction
    # -------------------------------------------------
    prompt = prompt_template.format(
        stabilizers_str=stabilizers_str,
        initial_circuit=initial_circuit,
        attempts=attempts,
        agent_files_dir=str(agent_files_dir),
    )

    print(prompt)

    prompt_agent(prompt, tools=[evaluate_optimization, final_circuit], model=model, timeout=timeout)

    # Check if result was populated by the agent
    if not result:
        return {"circuit": None, "evaluations": evaluations}

    print('done.')
    return {"circuit": result, "evaluations": evaluations}


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


if __name__ == "__main__":
    main()
