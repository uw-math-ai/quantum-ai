"""
Agent A wrapper: uses FoundryCircuitGenerator to produce circuits.
"""

from typing import List, Optional

from foundry_wrapper import FoundryCircuitGenerator


class CircuitGeneratorAgent:
    def __init__(
        self,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ):
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.model = FoundryCircuitGenerator()

    def generate(self, stabilizers: List[str]) -> str:
        return self.model.generate_circuit(
            stabilizers,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )

    def generate_batch(self, stabilizers_batch: List[List[str]]) -> List[str]:
        return self.model.generate_batch(
            stabilizers_batch,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )


if __name__ == "__main__":
    agent = CircuitGeneratorAgent()
    test_stabilizers = ["XXX", "ZZI", "IZZ"]
    print(agent.generate(test_stabilizers))
