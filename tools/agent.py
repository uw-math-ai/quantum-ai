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
from check_error_propagation import check_fault_tolerance, ft_score
from circuit_metric import is_strictly_more_optimal, compute_metrics

load_dotenv()

generated_ft_circuits = []

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
    distance: int, qubits: list[int], attempts: int | None = 3, timeout: int | None = 60, *, model: str) -> tuple[stim.Circuit, list[dict]] | None:
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
        score = ft_score(circuit.circuit, circuit.data_qubits, ancillas, distance, 1.0)

        # Append candidate to list
        all_candidates.append({
            "circuit": str(parsed),
            "ft_score": score
        })

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

    # Sylvie's prompt
    # prompt = f"""
    # You are a quantum error correction assistant.

    # Consider the following inputs and do not proceed unless all are provided:
    #     A quantum circuit 
    #     ```
    #     {non_ft_circuit} 
    #     ```
    #     described in Stim format, which prepares a state that is not necessarily fault-tolerant.
    #     The distance of the code being prepared 
    #     ```
    #     {distance}
    #     ```
    #     The circuit stabilizers 
    #     ```
    #     {stabilizers_str}
    #     ```
    # Task: Generate a fault tolerant version of 
    # ```
    # {non_ft_circuit}
    # ``` that preserves the given stabilizers in 
    # ```
    # {stabilizers_str}
    # ```.

    # Fault tolerance:
    # - A fault is a location in the circuit where there is an unexpected disruption (X, Y, Z Pauli gate) that alters the circuit's intended state in an undesired way.
    # - A circuit is fault tolerant if any fault propagates to less than floor(({distance} - 1)/ 2) data qubits
    # - A circuit is also fault tolerant if a fault that propagates to greater than or equal to floor(({distance} - 1)/2) data qubits triggers a flag ancilla that indicates a failure of the circuit. 
    # - You may use flag ancillas to detect high-weight fault propagation. (put more about how to use flags)
    # - See https://mqt.readthedocs.io/projects/qecc/en/latest/StatePrep.html for guidance on the fault tolerant transformation

    # Transformation guidelines:
    # - Do not change the structure of the original circuit. You may add ancillas, but do not reorder gates on the original data qubits. 
    # - Introduce additional ancilla qubits if necessary to reduce error propagation.
    # - The resulting circuit must prepare a state stabilized by all generators in {stabilizers_str}. 
    # - All ancilla qubits must be initialized in the |0⟩ state and measured at the end of the circuit. 

    # Tooling / output rules:  
    # - You may call validate_circuit to evaluate a candidate circuit. IMPORTANT: one call to validate_circuit counts as ONE attempt. 
    # - You have a total budget of 5 attempt(s) = at most 5 calls to validate_circuit.
    # - Keep track of the best circuit seen so far using the following priority:
    #     1) Preserve all stabilizers.
    #     2) Maximize fault tolerance score.
    #     3) Prefer shorter/simpler circuits.
    # - You should iteratively propose a circuit, call validate_circuit, then revise. Use the error propagation results to help improve the fault tolerance of each proposed circuit. 
    # - If all stabilizers are preserved (every result is true) and the circuit is fault tolerant (the result is true), you have found the correct circuit - immediately call return_result with it. You do NOT need to use all attempts.
    # -  The new fault tolerant circuit output must be a plain string, for example
    #     \"H 0
    #    CX 0 3\"
    # - When you are out of attempts, call return_result with the BEST circuit you found, even if it is not perfect. This means that all of the stabilizers are stabilized and the fault tolerance score is higher than any of the other circuits. 
    # - Do NOT call or rely on any repository tools besides validate_circuit and return_result.
    # - If you need to write any temporary or scratch files, write them into the directory: {agent_files_dir}
    # - Do NOT output Markdown code fences, prose, or extra markers.

    # Do not end the conversation without calling return_result.
    # """

    # Cordelia's prompt
    prompt = f"""
        You are an assistant that edits quantum circuits. You will edit a non-fault tolerant circuit and aim at increasing the fault tolerant score. 

        Input: a Stim circuit C {non_ft_circuit}, the distance of the code {distance}, a list of the stabilizers {stabilizers_str}.

        Setup: Let $d$ be the distance of the codes, {distance}, and let $t$ be the correctable threshold: 
        [
        t = \\left\\lfloor\\frac{{d-1}}{2}\\right\\rfloor.
        ]

        Let \\mathrm{{spots}}(C) be the set of valid fault locations in C where a single-qubit Pauli fault can occur. For each l \\in \\mathrm{{spots}}(C) and P \\in {{X,Y,Z}}, let C[l \\leftarrow P] denote the circuit obtained from C by inserting P at location l. Define
        [
        \\mathcal{{S}}(C) = {{ C[l \\leftarrow P] : l \\in \\mathrm{{spots}}(C),; P \\in {{X,Y,Z}}  }}.
        ]
        Let (E(C', C)) be the number of errors in (C') compared with (C) after propagation computed by check_error_propogation.py.

        Flag gadget: A flag qubit $f$ is an extra ancilla qubit added to a circuit to detect harmful error propagation. It is coupled to the data qubits so that it is triggered, meaning it is measured with eigenvalue -1, if and only if a fault causes an error that propagates to more data qubits than the code can correct, that is, beyond the correctable threshold t. You can find flag qubit strategies in https://arxiv.org/pdf/2408.11894

        We now setup the fault-tolerance score. Let \\pi \\in {{0,1}} be a rule indicating whether the result from one execution should be accepted. If a circuit C contains no flag, set \\pi(C) =1.
        For \\mathcal{{S}}(C), let \\mathcal{{T}}(\\mathcal{{S}}(C)) denote the set of all circuits in \\mathcal{{S}}(C) with error larger than the correctable threshold t comparing with C, i.e.
        [\\mathcal{{T}}(\\mathcal{{S}}(C)) := {{ C \\in \\mathcal{{S}} \\ | \\ E(C',C) > t }}.]

        Then the fault-tolerance score is defined by
        [\\mathrm{{FT}}(C) = \\begin{{cases}} 
        0 & \\text{{if }} \\pi(C) \\neq 1 \\\\
        \\displaystyle{{1-\\frac{{1}}{{|\\mathcal{{T}}(\\mathcal{{S}}(C))|}}
        \\sum_{{C'\\in \\mathcal{{S}}(C)}}
        \\mathbf{{1}}!\\left{{\\pi(C')=1 ,\\wedge, E(C', C)>t\\right}}}} & \\text{{if }} \\pi(C) = 1 \\text{{ and }}  \\mathcal{{T}}(\\mathcal{{S}}(C)) \\neq \\emptyset  \\\\
        1 & \\text{{if }} \\pi(C) = 1 \\text{{ and }}  \\mathcal{{T}}(\\mathcal{{S}}(C)) = \\emptyset.
        \\end{{cases}}
        ]

        Task: Modify C to a new stim circuit $\\hat{{C}}$ that has the same output and stabilizes the same code space as C (you can use functions in check_stabilizers.py to check for stabilizer). You can adjust the gates and/or add flags and ancilla qubits. Aim to increase \\mathrm{{FT}}(\\hat{{C}}) at each attempt; keep the maximal \\mathrm{{FT}}(\\hat{{C}}) and \\hat{{C}} you found so far. Stop and output if \\mathrm{{FT}}(\\hat{{C}}) reaches 1. 

        You have 10 attempts. If you run out of attempts, output the maximal \\mathrm{{FT}}(\\hat{{C}}) you found and the corresponding \\hat{{C}}.
        """

    prompt_agent(prompt, tools=[validate_circuit, return_result], model=model, timeout=timeout)

    if result is None:
        return None, all_candidates

    return result, all_candidates


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
