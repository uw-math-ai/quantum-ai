"""
Foundry circuit generator: wraps FoundryCircuitGenerator for batch circuit generation.
"""

from typing import List

from foundry_wrapper import FoundryCircuitGenerator


class FoundryCircuitGeneratorAgent:
    def __init__(
        self,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ):
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.model = FoundryCircuitGenerator()

    def generate_circuit(self, stabilizers: List[str]) -> str:
        return self.model.generate_circuit(
            stabilizers,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )

    def generate_batch_circuits(self, stabilizers_batch: List[List[str]]) -> List[str]:
        return self.model.generate_batch(
            stabilizers_batch,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )


if __name__ == "__main__":
    agent = FoundryCircuitGeneratorAgent()
    test_stabilizers = ["XXX", "ZZI", "IZZ"]
    print(agent.generate_circuit(test_stabilizers))
