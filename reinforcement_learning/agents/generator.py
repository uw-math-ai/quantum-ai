"""
LLM circuit generator: loads a HuggingFace LLM and generates quantum circuits.
Captures log probabilities for policy gradient RL training.
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import List, Tuple
import numpy as np


class LlmCircuitGenerator:
    """Generate quantum circuits with log probability tracking for RL."""
    
    def __init__(
        self,
        model_name: str = "local_model",  # Use local_model as default
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        temperature: float = 0.2,
        max_tokens: int = 512,
    ):
        self.device = device
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        print(f"Loading model {model_name} on {device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

        device_map = "auto" if device.startswith("cuda") else None
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map=device_map,
            torch_dtype=torch.float16 if device.startswith("cuda") else torch.float32,
            trust_remote_code=True,
        )
        if device_map is None:
            self.model.to(device)
        self.model.eval()
        
        # Set pad token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        print(f"Model loaded successfully on {device}")
    
    def _format_prompt(self, stabilizers: List[str]) -> str:
        """Format stabilizers into a prompt for the model."""
        stab_str = "\n".join(stabilizers)
        prompt = f"""Generate a quantum circuit that prepares a state satisfying these stabilizers:
{stab_str}

Circuit:"""
        return prompt

    def generate_batch_circuits(
        self,
        stabilizers_batch: List[List[str]],
    ) -> Tuple[List[str], List[str]]:
        """
        Generate circuits for a batch and return (circuits, prompts).

        Returns:
            (circuits, prompts)
        """
        circuits = []
        prompts = []

        for stabilizers in stabilizers_batch:
            prompt = self._format_prompt(stabilizers)
            prompts.append(prompt)

            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                padding=True,
            ).to(next(self.model.parameters()).device)

            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_new_tokens=self.max_tokens,
                    temperature=self.temperature,
                    top_p=0.95,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                )

            generated_ids = outputs
            prompt_len = inputs.input_ids.shape[1]
            generated_text = self.tokenizer.decode(
                generated_ids[0][prompt_len:],
                skip_special_tokens=True
            )
            circuits.append(generated_text.strip())

        return circuits, prompts

    def compute_logprobs(
        self,
        prompts: List[str],
        completions: List[str],
    ) -> torch.Tensor:
        """
        Compute sum log-probabilities of completions given prompts.

        Returns:
            Tensor of shape (batch,) with log-prob sums.
        """
        device = next(self.model.parameters()).device
        log_probs = []

        for prompt, completion in zip(prompts, completions):
            prompt_ids = self.tokenizer(
                prompt,
                return_tensors="pt",
                add_special_tokens=True,
            ).input_ids.to(device)

            completion_ids = self.tokenizer(
                completion,
                return_tensors="pt",
                add_special_tokens=False,
            ).input_ids.to(device)

            if completion_ids.shape[1] == 0:
                log_probs.append(torch.tensor(0.0, device=device))
                continue

            input_ids = torch.cat([prompt_ids, completion_ids], dim=1)
            prompt_len = prompt_ids.shape[1]

            outputs = self.model(input_ids)
            logits = outputs.logits

            # logits predict next token; align completion tokens
            start = prompt_len
            end = input_ids.shape[1]
            logits_slice = logits[:, start - 1:end - 1, :]
            target_tokens = input_ids[:, start:end]

            log_prob_tokens = torch.nn.functional.log_softmax(logits_slice, dim=-1)
            token_log_probs = log_prob_tokens.gather(2, target_tokens.unsqueeze(-1)).squeeze(-1)
            log_probs.append(token_log_probs.sum(dim=1).squeeze(0))

        return torch.stack(log_probs)
    
    def generate_with_logprobs(
        self,
        stabilizers: List[str],
    ) -> Tuple[str, float]:
        """
        Generate a circuit and return (circuit_str, mean_log_prob).
        
        Returns:
            (circuit_str, mean_log_prob)
        """
        prompt = self._format_prompt(stabilizers)
        
        # Tokenize
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            padding=True,
        ).to(self.device)
        
        input_ids = inputs.input_ids
        prompt_len = input_ids.shape[1]
        
        # Generate with output_scores
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids,
                max_new_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=0.95,
                output_scores=True,
                return_dict_in_generate=True,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        
        generated_ids = outputs.sequences
        generated_text = self.tokenizer.decode(
            generated_ids[0][prompt_len:],
            skip_special_tokens=True
        )
        
        # Extract circuit text (keep full multi-line circuit if present)
        circuit_str = generated_text.strip()
        
        # Compute mean log probability
        # scores contains log probabilities for each generated token
        scores = outputs.scores  # List of (batch_size, vocab_size)
        
        if len(scores) > 0:
            # Get log prob of sampled token at each step
            log_probs = []
            for i, score in enumerate(scores):
                # score shape: (1, vocab_size)
                # Get the token ID that was sampled
                sampled_token_id = generated_ids[0, prompt_len + i]
                log_prob = torch.nn.functional.log_softmax(score, dim=-1)
                token_log_prob = log_prob[0, sampled_token_id].item()
                log_probs.append(token_log_prob)
            
            mean_log_prob = np.mean(log_probs)
        else:
            mean_log_prob = 0.0
        
        return circuit_str, float(mean_log_prob)
    
    def generate_batch_circuits_with_logprobs(
        self,
        stabilizers_batch: List[List[str]],
    ) -> Tuple[List[str], List[float]]:
        """
        Generate circuits for a batch and return (circuits, log_probs).
        
        Returns:
            (circuits, log_probs) where log_probs are mean log prob per circuit
        """
        circuits = []
        log_probs = []
        
        for stabilizers in stabilizers_batch:
            circuit, log_prob = self.generate_with_logprobs(stabilizers)
            circuits.append(circuit)
            log_probs.append(log_prob)
        
        return circuits, log_probs


if __name__ == "__main__":
    agent = LlmCircuitGenerator()
    test_stabs = ["XXX", "ZZI", "IZZ"]
    
    print("Generating single circuit...")
    circuit, log_prob = agent.generate_with_logprobs(test_stabs)
    print(f"Circuit: {circuit}")
    print(f"Log prob: {log_prob:.4f}")
    
    print("\nGenerating batch...")
    circuits, log_probs = agent.generate_batch_circuits_with_logprobs([test_stabs, test_stabs])
    for c, lp in zip(circuits, log_probs):
        print(f"Circuit: {c[:30]}... | Log prob: {lp:.4f}")
