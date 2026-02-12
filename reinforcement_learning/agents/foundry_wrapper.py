"""
Azure AI Foundry (Azure OpenAI-compatible) circuit generator wrapper.

Required env vars:
- FOUNDRY_ENDPOINT (e.g., https://<resource>.openai.azure.com)
- FOUNDRY_API_KEY
- FOUNDRY_DEPLOYMENT (deployment name)
Optional:
- FOUNDRY_API_VERSION (default: 2024-02-15-preview)
- FOUNDRY_URL (full URL to chat/completions or responses endpoint)
"""

import os
import sys
import json
from typing import List, Dict, Optional

# Add workspace root to path to resolve module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import requests

from tools.check_stabilizers import check_stabilizers


def _load_env_from_tools() -> None:
    env_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "tools", ".env")
    )
    if not os.path.exists(env_path):
        return
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                if key and key not in os.environ:
                    os.environ[key] = value
    except Exception:
        return


class FoundryCircuitGenerator:
    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        deployment: Optional[str] = None,
        api_version: Optional[str] = None,
        url: Optional[str] = None,
        timeout_s: int = 60,
    ):
        _load_env_from_tools()
        self.url = url or os.getenv("FOUNDRY_URL")
        self.endpoint = endpoint or os.getenv("FOUNDRY_ENDPOINT")
        self.api_key = api_key or os.getenv("FOUNDRY_API_KEY")
        self.deployment = deployment or os.getenv("FOUNDRY_DEPLOYMENT")
        self.api_version = api_version or os.getenv("FOUNDRY_API_VERSION", "2024-02-15-preview")
        self.timeout_s = timeout_s

        missing = [k for k, v in {
            "FOUNDRY_API_KEY": self.api_key,
        }.items() if not v]
        if not self.url:
            missing += [k for k, v in {
                "FOUNDRY_ENDPOINT": self.endpoint,
                "FOUNDRY_DEPLOYMENT": self.deployment,
            }.items() if not v]
        elif self._infer_mode(self.url) == "responses" and not self.deployment:
            missing += ["FOUNDRY_DEPLOYMENT"]
        if missing:
            raise ValueError(f"Missing required config: {', '.join(missing)}")

    def _build_url(self) -> str:
        if self.url:
            return self.url
        base = self.endpoint.rstrip("/")
        return f"{base}/openai/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"

    def _infer_mode(self, url: str) -> str:
        return "responses" if "/responses" in url else "chat"

    def _build_request_body(self, stabilizers: List[str], max_tokens: int, temperature: float, mode: str) -> Dict:
        messages = self._build_prompt(stabilizers)
        if mode == "responses":
            responses_input = [
                {
                    "role": m["role"],
                    "content": [{"type": "input_text", "text": m["content"]}],
                }
                for m in messages
            ]
            return {
                "model": self.deployment,
                "input": responses_input,
                "max_output_tokens": max_tokens,
                "text": {
                    "format": {"type": "text"},
                    "verbosity": "medium",
                },
                "reasoning": {"effort": "medium"},
            }
        return {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

    def _extract_text(self, data: Dict) -> str:
        if "choices" in data and data["choices"]:
            content = data["choices"][0].get("message", {}).get("content")
            if content:
                return content.strip()
        if "output_text" in data and data["output_text"]:
            return data["output_text"].strip()
        if "output" in data and data["output"]:
            for item in data["output"]:
                if "output_text" in item and item["output_text"]:
                    return item["output_text"].strip()
                content = item.get("content", [])
                for part in content:
                    text = part.get("text")
                    if text:
                        return text.strip()
        raise ValueError(f"No text content found in response: {data}")

    def _build_prompt(self, stabilizers: List[str]) -> List[Dict[str, str]]:
        system = (
            "You are an expert quantum circuit designer specializing in fault-tolerant codes. "
            "Output ONLY valid Stim instructions. No explanations, no markdown, no extra text."
        )
        
        num_qubits = len(stabilizers[0]) if stabilizers else 1
        stab_str = ", ".join(stabilizers)
        
        user = (
            f"Design a quantum circuit that creates a state stabilized by:\n"
            f"{stab_str}\n\n"
            f"Constraints:\n"
            f"- Use only: H, X, Z, CX, CZ, M (measurement)\n"
            f"- {num_qubits} qubits (indexed 0 to {num_qubits-1})\n"
            f"- Stabilizer notation: X/Z/I means Pauli operator on that qubit\n"
            f"- Output format: one instruction per line, no extra whitespace\n\n"
            f"Output ONLY the circuit:"
        )
        
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

    def generate_circuit(self, stabilizers: List[str], max_tokens: int = 2048, temperature: float = 0.2) -> str:
        url = self._build_url()
        mode = self._infer_mode(url)
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key,
        }

        attempts = 0
        current_max = max_tokens
        while attempts < 2:
            body = self._build_request_body(stabilizers, current_max, temperature, mode)
            resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=self.timeout_s)
            if not resp.ok:
                raise ValueError(f"Request failed ({resp.status_code}): {resp.text}")
            data = resp.json()

            if mode == "responses":
                status = data.get("status")
                if status and status != "completed":
                    reason = (data.get("incomplete_details") or {}).get("reason")
                    if reason == "max_output_tokens":
                        current_max = min(current_max * 2, 8192)
                        attempts += 1
                        continue
                    raise ValueError(f"Response incomplete: {data.get('incomplete_details', data)}")

            return self._extract_text(data)

        raise ValueError("Response incomplete after retries: max_output_tokens")

    def generate_batch(
        self,
        stabilizers_batch: List[List[str]],
        max_tokens: int = 2048,
        temperature: float = 0.2,
    ) -> List[str]:
        outputs = []
        for stabilizers in stabilizers_batch:
            outputs.append(self.generate_circuit(stabilizers, max_tokens=max_tokens, temperature=temperature))
        return outputs


def _load_variants_from_env() -> List[Dict[str, str]]:
    """
    Load model variants from env.

    Supported formats:
    - FOUNDRY_MODEL_VARIANTS: JSON list of objects with keys: name, deployment, api_version, url (optional)
    - FOUNDRY_DEPLOYMENTS: comma-separated deployment names (uses FOUNDRY_API_VERSION for all)
    """
    variants_json = os.getenv("FOUNDRY_MODEL_VARIANTS")
    if variants_json:
        try:
            data = json.loads(variants_json)
            if isinstance(data, list):
                return data
        except Exception:
            pass

    deployments = os.getenv("FOUNDRY_DEPLOYMENTS")
    if deployments:
        api_version = os.getenv("FOUNDRY_API_VERSION", "2024-02-15-preview")
        return [
            {"name": d.strip(), "deployment": d.strip(), "api_version": api_version}
            for d in deployments.split(",")
            if d.strip()
        ]

    return []


def run_model_trials(
    variants: List[Dict[str, str]],
    stabilizers: List[str],
    trials: int = 10,
    max_tokens: int = 2048,
    temperature: float = 0.,
) -> Dict[str, Dict[str, float]]:
    """
    Run multiple trials per model variant and compute success rate.

    Success = circuit parses + all stabilizers satisfied.
    """
    results: Dict[str, Dict[str, float]] = {}

    for variant in variants:
        name = variant.get("name") or variant.get("deployment") or "unknown"
        deployment = variant.get("deployment")
        api_version = variant.get("api_version")
        url = variant.get("url")

        successes = 0
        failures = 0

        try:
            generator = FoundryCircuitGenerator(
                deployment=deployment,
                api_version=api_version,
                url=url,
            )
        except Exception as e:
            results[name] = {
                "successes": 0,
                "failures": trials,
                "success_rate": 0.0,
                "error": str(e),
            }
            continue

        for trial_idx in range(trials):
            try:
                circuit = generator.generate_circuit(
                    stabilizers,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                if not circuit.strip():
                    failures += 1
                    print(f"Trial {trial_idx + 1}: EMPTY circuit")
                    continue

                checks = check_stabilizers(circuit, stabilizers)
                print(f"Trial {trial_idx + 1} checks: {checks}")
                if checks and all(checks.values()):
                    successes += 1
                else:
                    failures += 1   
            except Exception as e:
                failures += 1
                print(f"Trial {trial_idx + 1} ERROR: {str(e)[:150]}")
        results[name] = {
            "successes": successes,
            "failures": failures,
            "success_rate": successes / max(1, trials),
        }

    return results


if __name__ == "__main__":
    # Multi-model benchmark (requires env vars to be set):
    # FOUNDRY_ENDPOINT, FOUNDRY_API_KEY, plus either:
    # - FOUNDRY_MODEL_VARIANTS (JSON list)
    # - FOUNDRY_DEPLOYMENTS (comma-separated)

    # Load environment variables from .env file
    _load_env_from_tools()

    test_stabilizers = ["XXX", "ZZI", "IZZ"]
    variants = _load_variants_from_env()

    if not variants:
        # Fallback to a single deployment if no variants provided
        generator = FoundryCircuitGenerator()
        circuit = generator.generate_circuit(test_stabilizers, temperature=0.1)
        print("Generated circuit:\n")
        print(circuit)
    else:
        results = run_model_trials(
            variants,
            stabilizers=test_stabilizers,
            trials=10,
            max_tokens=512,
            temperature=0.1,
        )
        print("\nModel success rates:")
        for name, stats in results.items():
            if "error" in stats:
                print(f"- {name}: ERROR ({stats['error']})")
                continue
            print(
                f"- {name}: {int(stats['successes'])}/{int(stats['successes'] + stats['failures'])} "
                f"({stats['success_rate']*100:.1f}%)"
            )
