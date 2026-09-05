#%%
import os
import stim
import asyncio
import inspect
import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pathlib import Path

from check_stabilizers import check_stabilizers
from check_error_propagation import check_fault_tolerance, ft_score
from circuit_metric import is_strictly_more_optimal

load_dotenv(Path(__file__).parent / ".env")

HARNESS_CHOICES = ("openai", "anthropic", "copilot")


@dataclass
class Tool:
    name: str
    description: str
    parameter_model: type[BaseModel]
    callback: object


def define_tool(description: str):
    """Adapt a Pydantic-backed Python callback to a provider-neutral tool."""
    def decorator(callback):
        parameter = next(iter(inspect.signature(callback).parameters.values()))
        parameter_model = parameter.annotation
        if not isinstance(parameter_model, type) or not issubclass(parameter_model, BaseModel):
            raise TypeError(f"Tool '{callback.__name__}' must accept a Pydantic model")
        return Tool(
            name=callback.__name__,
            description=description,
            parameter_model=parameter_model,
            callback=callback,
        )
    return decorator

# Load system prompt template once at module startup
with open("tools/system_prompt.txt", "r") as f:
    SYSTEM_PROMPT_TEMPLATE = f.read()

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



def _prompt_openai(
    prompt: str,
    system_message: str = "",
    tools: list[Tool] | None = None,
    model: str = "gpt-5.2-codex",
    timeout: int | None = 60,
) -> str:
    """Prompt an OpenAI model through Responses API and execute local tools."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required to run Codex directly")

    timeout_seconds = timeout if timeout is not None else 600
    response_tools = [
        {
            "type": "function",
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameter_model.model_json_schema(),
        }
        for tool in tools or []
    ]

    def request_response(payload: dict, request_number: int) -> dict:
        input_items = payload["input"]
        input_kind = "prompt" if isinstance(input_items, str) else "tool output"
        started_at = datetime.now()
        print(f"[openai] request {request_number}: sending {input_kind}", flush=True)
        request = urllib.request.Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                result = json.load(response)
            elapsed = (datetime.now() - started_at).total_seconds()
            output_types = ", ".join(item.get("type", "unknown") for item in result.get("output", []))
            print(f"[openai] request {request_number}: received {output_types or 'empty response'} in {elapsed:.1f}s", flush=True)
            return result
        except urllib.error.HTTPError as error:
            details = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI Responses API returned HTTP {error.code}: {details}") from error
        except urllib.error.URLError as error:
            raise RuntimeError(f"OpenAI Responses API request failed: {error.reason}") from error

    response = request_response({
        "model": model,
        "instructions": system_message,
        "input": prompt,
        "tools": response_tools,
        "tool_choice": "required" if response_tools else "auto",
        "parallel_tool_calls": False,
    }, request_number=1)
    tool_map = {tool.name: tool for tool in tools or []}

    for _ in range(100):
        calls = [item for item in response.get("output", []) if item.get("type") == "function_call"]
        if not calls:
            messages = []
            for item in response.get("output", []):
                if item.get("type") != "message":
                    continue
                messages.extend(
                    content.get("text", "")
                    for content in item.get("content", [])
                    if content.get("type") == "output_text"
                )
            return "\n".join(messages)

        tool_outputs = []
        for call in calls:
            tool = tool_map.get(call["name"])
            print(f"[openai] tool call: {call['name']}", flush=True)
            if tool is None:
                tool_result = {"error": f"Unknown tool: {call['name']}"}
            else:
                try:
                    arguments = tool.parameter_model.model_validate_json(call["arguments"])
                    tool_result = tool.callback(arguments)
                except Exception as error:
                    tool_result = {"error": str(error)}
            print(f"[openai] tool result: {call['name']}", flush=True)
            tool_outputs.append({
                "type": "function_call_output",
                "call_id": call["call_id"],
                "output": json.dumps(tool_result, default=str),
            })

        response = request_response({
            "model": model,
            "previous_response_id": response["id"],
            "input": tool_outputs,
            "tools": response_tools,
            "tool_choice": "auto",
            "parallel_tool_calls": False,
        }, request_number=_ + 2)

    raise RuntimeError("OpenAI exceeded the maximum number of tool-call rounds")


def _prompt_anthropic(
    prompt: str,
    system_message: str,
    tools: list[Tool] | None,
    model: str,
    timeout: int | None,
) -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is required for the anthropic harness")

    timeout_seconds = timeout if timeout is not None else 600
    anthropic_tools = [
        {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.parameter_model.model_json_schema(),
        }
        for tool in tools or []
    ]
    tool_map = {tool.name: tool for tool in tools or []}
    messages = [{"role": "user", "content": prompt}]

    def request_message(payload: dict, request_number: int) -> dict:
        input_kind = "prompt" if request_number == 1 else "tool output"
        started_at = datetime.now()
        print(f"[anthropic] request {request_number}: sending {input_kind}", flush=True)
        request = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                result = json.load(response)
            elapsed = (datetime.now() - started_at).total_seconds()
            content_types = ", ".join(item.get("type", "unknown") for item in result.get("content", []))
            print(f"[anthropic] request {request_number}: received {content_types or 'empty response'} in {elapsed:.1f}s", flush=True)
            return result
        except urllib.error.HTTPError as error:
            details = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Anthropic Messages API returned HTTP {error.code}: {details}") from error
        except urllib.error.URLError as error:
            raise RuntimeError(f"Anthropic Messages API request failed: {error.reason}") from error

    for _ in range(100):
        response = request_message({
            "model": model,
            "max_tokens": 8192,
            "system": system_message,
            "messages": messages,
            "tools": anthropic_tools,
        }, request_number=_ + 1)
        content = response.get("content", [])
        calls = [item for item in content if item.get("type") == "tool_use"]
        if not calls:
            return "\n".join(item["text"] for item in content if item.get("type") == "text")

        tool_results = []
        for call in calls:
            tool = tool_map.get(call["name"])
            print(f"[anthropic] tool call: {call['name']}", flush=True)
            if tool is None:
                tool_result = {"error": f"Unknown tool: {call['name']}"}
            else:
                try:
                    arguments = tool.parameter_model.model_validate(call["input"])
                    tool_result = tool.callback(arguments)
                except Exception as error:
                    tool_result = {"error": str(error)}
            print(f"[anthropic] tool result: {call['name']}", flush=True)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": call["id"],
                "content": json.dumps(tool_result, default=str),
            })

        messages.append({"role": "assistant", "content": content})
        messages.append({"role": "user", "content": tool_results})

    raise RuntimeError("Anthropic exceeded the maximum number of tool-call rounds")


def _prompt_copilot(
    prompt: str,
    system_message: str,
    tools: list[Tool] | None,
    model: str,
    timeout: int | None,
) -> str:
    try:
        from copilot import CopilotClient
        from copilot.generated.session_events import SessionEventType
        from copilot.tools import define_tool as define_copilot_tool
    except ImportError as error:
        raise RuntimeError("Install github-copilot-sdk to use the copilot harness") from error

    copilot_tools = [
        define_copilot_tool(description=tool.description)(tool.callback)
        for tool in tools or []
    ]

    async def run() -> str:
        client = CopilotClient(options={"auto_start": True})
        try:
            session = await client.create_session({
                "on_permission_request": lambda _, __: {"kind": "approved", "rules": []},
                "model": model,
                "tools": copilot_tools,
                "system_message": {"content": system_message},
            })
            response = ""

            def handle_event(event):
                nonlocal response
                if event.type == SessionEventType.ASSISTANT_MESSAGE and event.data.content:
                    print(event.data.content)
                    response = event.data.content

            session.on(handle_event)
            started_at = datetime.now()
            print("[copilot] request 1: sending prompt", flush=True)
            await session.send_and_wait(options={"prompt": prompt}, timeout=timeout)
            elapsed = (datetime.now() - started_at).total_seconds()
            print(f"[copilot] request 1: completed in {elapsed:.1f}s", flush=True)
            return response
        finally:
            await client.stop()

    return asyncio.run(run())


def prompt_agent(
    prompt: str,
    system_message: str = "",
    tools: list[Tool] | None = None,
    model: str = "gpt-5.2-codex",
    timeout: int | None = 60,
    harness: str = "openai",
) -> str:
    """Run an agent via the selected provider harness and local verification tools."""
    if harness == "openai":
        return _prompt_openai(prompt, system_message, tools, model, timeout)
    if harness == "anthropic":
        return _prompt_anthropic(prompt, system_message, tools, model, timeout)
    if harness == "copilot":
        return _prompt_copilot(prompt, system_message, tools, model, timeout)
    choices = ", ".join(HARNESS_CHOICES)
    raise ValueError(f"Unknown harness '{harness}'. Choose one of: {choices}")

def generate_ft_state_prep(stabilizers: list[str], non_ft_circuit: str, 
    distance: int, attempts: int | None = 3, timeout: int | None = 60, *, model: str,
    prompt_file: str = "B3/prompts/ft_state_prep_prompt0.txt", harness: str = "openai") -> tuple[stim.Circuit, list[dict]] | None:
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
        # attempts=attempts,
        # agent_files_dir=agent_files_dir
    )

    system_message = SYSTEM_PROMPT_TEMPLATE.format(
        N=attempts,
        agent_files_dir=agent_files_dir,
        tools="validate_circuit, return_result",
        return_tool="return_result"
    )

    print(prompt)

    prompt_agent(prompt, system_message=system_message, tools=[validate_circuit, return_result], model=model, timeout=timeout, harness=harness)

    if result is None:
        return None, all_candidates

    return result, all_candidates


def generate_state_prep(stabilizers: list[str], *, model: str, attempts: int = 1, timeout: int | None = 600, prompt_file: str = "rq1/prompts/state_prep_prompt4.txt", harness: str = "openai") -> stim.Circuit | None:
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

    system_message = SYSTEM_PROMPT_TEMPLATE.format(
        N=attempts,
        agent_files_dir=agent_files_dir,
        tools="check_stabilizers_tool, final_circuit",
        return_tool="final_circuit"
    )

    print(prompt)

    prompt_agent(prompt, system_message=system_message, tools=[check_stabilizers_tool, final_circuit], model=model, timeout=timeout, harness=harness)

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
    harness: str = "openai",
) -> dict:
    """
    Optimize an existing Clifford circuit while preserving stabilizers.
    Uses lexicographic rule: (two_qubit_gates, volume, depth).

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

    repo_root = Path(__file__).resolve().parents[1]
    run_id = datetime.now().strftime("%y%m%d.%H%M%S")
    agent_files_dir = repo_root / "rq3" / "data" / model / "agent_files" / run_id
    agent_files_dir.mkdir(parents=True, exist_ok=True)

    result = None
    best_valid_circuit = None   # best valid+better circuit seen across all evaluations
    best_valid_metrics = None   # its (two_qubit_gates, volume, depth) tuple
    evaluations = []

    @define_tool(description=(
        "Evaluate a candidate Stim circuit for correctness AND optimization.\n\n"
        "This is the primary evaluation tool. It performs two checks in order:\n\n"
        "1. STABILIZER PRESERVATION – simulates the circuit with a TableauSimulator\n"
        "   to verify that every target stabilizer has expectation +1. If any\n"
        "   stabilizer is not preserved the circuit is INVALID.\n\n"
        "2. OPTIMIZATION COMPARISON – compares the candidate against the baseline\n"
        "   using a strict lexicographic rule on three integer metrics:\n"
        "     a. two_qubit_gates – total count of ALL two-qubit gates (CX, CZ, SWAP, etc.) (primary).\n"
        "     b. volume          – total gate count in the volume gate set (secondary).\n"
        "     c. depth           – circuit depth (tertiary).\n"
        "   A candidate is 'strictly better' only when the tuple\n"
        "   (cand.two_qubit_gates, cand.volume, cand.depth) is lexicographically\n"
        "   less than the baseline tuple. Equal tuples are NOT an improvement.\n\n"
        "Input:\n"
        "  - candidate: raw Stim circuit text (no Markdown fences). Must be\n"
        "    parseable by stim.Circuit.\n\n"
        "Output (on success):\n"
        "  {\n"
        "    'preserved_stabilizers': <int>  (number of stabilizers preserved out of total),\n"
        "    'valid': true/false             (true when ALL stabilizers are preserved),\n"
        "    'candidate': { 'two_qubit_gates': int, 'volume': int, 'depth': int, ... },\n"
        "    'baseline':  { 'two_qubit_gates': int, 'volume': int, 'depth': int, ... },\n"
        "    'better': true/false\n"
        "  }\n\n"
        "Output (on parse / error): { 'error': <string> }\n\n"
        "Usage guidance:\n"
        "  - Call this tool to check every candidate before submitting via final_circuit.\n"
        "  - When valid == true AND better == true, update your best-so-far and keep\n"
        "    optimizing — do NOT stop early. Use all available attempts.\n"
        "  - Prioritize reducing two_qubit_gates first, then volume, then depth."
    ))
    def evaluate_optimization(params: OptimizeParam) -> dict:
        try:
            stim.Circuit(params.candidate)
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
            f"[OPT] 2Q: {cand['two_qubit_gates']} (base {base['two_qubit_gates']}), "
            f"VOL: {cand['volume']} (base {base['volume']}), "
            f"DEPTH: {cand['depth']} (base {base['depth']}) "
            f"{'✓' if better else '✗'} | "
            f"stabilizers: {preserved}/{len(stab_results)} "
            f"{'✓' if all_preserved else '✗'}"
        )

        eval_result = {
            "preserved_stabilizers": preserved,
            "valid": all_preserved,
            "candidate": cand,
            "baseline": base,
            "better": better,
        }

        # Track this evaluation for intermediate results
        evaluations.append({
            "circuit": params.candidate,
            **eval_result,
        })

        # Update best valid+better seen so far
        nonlocal best_valid_circuit, best_valid_metrics
        if all_preserved and better:
            candidate_key = (cand["two_qubit_gates"], cand["volume"], cand["depth"])
            if best_valid_metrics is None or candidate_key < best_valid_metrics:
                best_valid_circuit = params.candidate
                best_valid_metrics = candidate_key

        return eval_result


    @define_tool(description=(
        "Submit the final optimized Stim circuit.\n\n"
        "Call this tool only after exhausting ALL available attempts, with the best\n"
        "valid+better circuit found across all evaluate_optimization calls.\n\n"
        "This tool performs two validation checks:\n"
        "  1. Stabilizer preservation – every target stabilizer must be satisfied.\n"
        "  2. Strict optimization     – the circuit must be lexicographically better\n"
        "     than the baseline on (two_qubit_gates, volume, depth).\n\n"
        "If either check fails the submission is rejected.\n\n"
        "Input:\n"
        "  - stim_circuit: raw Stim circuit text (no Markdown fences, no prose).\n\n"
        "Output:\n"
        "  - On success: confirmation message.\n"
        "  - On failure: description of what went wrong.\n\n"
        "Best practice:\n"
        "  - Only call this once, after all attempts are exhausted.\n"
        "  - Submit the circuit with the lowest (two_qubit_gates, volume, depth) tuple\n"
        "    that was both valid and better."
    ))
    def final_circuit(params: FinalCircuitParam) -> str:
        nonlocal result, best_valid_circuit, best_valid_metrics

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
                f"2Q {cand['two_qubit_gates']} vs {base['two_qubit_gates']}, "
                f"VOL {cand['volume']} vs {base['volume']}, "
                f"DEPTH {cand['depth']} vs {base['depth']}"
            )
            return "Circuit is NOT strictly more optimal."

        cand = info["candidate"]
        candidate_key = (cand["two_qubit_gates"], cand["volume"], cand["depth"])

        # Accept only if this beats or matches the current best
        if best_valid_metrics is None or candidate_key <= best_valid_metrics:
            result = parsed
            best_valid_circuit = params.stim_circuit
            best_valid_metrics = candidate_key

        return "Final optimized circuit accepted."

    # -------------------------------------------------
    # Prompt Construction
    # -------------------------------------------------
    prompt = prompt_template.format(
        stabilizers_str=stabilizers_str,
        initial_circuit=initial_circuit,
        # attempts=attempts,
        # agent_files_dir=str(agent_files_dir),
    )

    system_message = SYSTEM_PROMPT_TEMPLATE.format(
        N=attempts,
        agent_files_dir=str(agent_files_dir),
        tools="evaluate_optimization, final_circuit",
        return_tool="final_circuit"
    )

    print(prompt)

    prompt_agent(prompt, system_message=system_message, tools=[evaluate_optimization, final_circuit], model=model, timeout=timeout, harness=harness)

    # Return best found: prefer what agent explicitly submitted via final_circuit,
    # but fall back to the best internally tracked if the agent failed to submit.
    print('done.')
    if result:
        return {"circuit": result, "evaluations": evaluations}
    if best_valid_circuit:
        return {"circuit": stim.Circuit(best_valid_circuit), "evaluations": evaluations}
    return {"circuit": None, "evaluations": evaluations}


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
    model = "gpt-4.1"
    # model = "claude-opus-4.6"
    # model = "claude-sonnet-4.5"
    # model = "gemini-3-pro-preview"
    # model = "gpt-5.2"
    attempts = 10
    result = generate_state_prep(stabilizers, model=model, attempts=attempts, timeout=6000)
    print(result)


if __name__ == "__main__":
    main()
