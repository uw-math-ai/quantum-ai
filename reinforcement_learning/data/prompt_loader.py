"""
Fast prompt loader for RL training.

Efficiently loads and samples stabilizer prompts from circuit_permute.jsonl
with O(1) random access using file offset indexing.
"""

import json
import random
from typing import List, Dict, Iterator, Optional, Tuple
import os


class PromptLoader:
    """
    Efficiently load and sample stabilizer prompts from JSONL dataset.
    
    Uses file offset indexing for fast random access without loading
    the entire dataset into memory.
    """
    
    def __init__(self, jsonl_path: str, preload: bool = False):
        """
        Initialize prompt loader.
        
        Args:
            jsonl_path: Path to circuit_permute.jsonl or similar JSONL file
            preload: If True, load all prompts into memory (faster but uses ~50MB RAM)
        """
        self.jsonl_path = jsonl_path
        self.preload = preload
        self._index = []  # List of (offset, source_code, d, num_qubits)
        self._data = []  # Preloaded data if preload=True
        
        if not os.path.exists(jsonl_path):
            raise FileNotFoundError(f"JSONL file not found: {jsonl_path}")
        
        self._build_index()
        
        if preload:
            self._load_all()
    
    def _build_index(self):
        """Build index of file offsets for fast random access."""
        with open(self.jsonl_path, 'r') as f:
            offset = 0
            for line in f:
                try:
                    data = json.loads(line)
                    source_code = data.get('source_code', 'unknown')
                    d = data.get('d', 1)
                    num_qubits = len(data['input_stabilizers'][0]) if data['input_stabilizers'] else 0
                    
                    self._index.append((offset, source_code, d, num_qubits))
                    offset += len(line.encode('utf-8'))
                except json.JSONDecodeError:
                    # Skip malformed lines
                    offset += len(line.encode('utf-8'))
                    continue
    
    def _load_all(self):
        """Load all prompts into memory."""
        with open(self.jsonl_path, 'r') as f:
            for line in f:
                try:
                    self._data.append(self._normalize_prompt(json.loads(line)))
                except json.JSONDecodeError:
                    continue
    
    def _load_at_offset(self, offset: int) -> Dict:
        """Load a single prompt at given file offset."""
        with open(self.jsonl_path, 'r') as f:
            f.seek(offset)
            line = f.readline()
            return self._normalize_prompt(json.loads(line))

    def _normalize_prompt(self, data: Dict) -> Dict:
        """Normalize prompt fields for downstream use."""
        output_circuit = data.get("output_circuit")
        if isinstance(output_circuit, str) and "\\n" in output_circuit:
            data["output_circuit"] = output_circuit.replace("\\n", "\n")
        return data
    
    def get_prompt(self, index: int) -> Dict:
        """
        Get prompt at specific index.
        
        Args:
            index: Index in dataset (0 to len-1)
            
        Returns:
            {
                "input_stabilizers": ["XZZXI", "IXZZX", ...],
                "source_code": "Perfect 5-Qubit Code",
                "d": 3,
                "output_circuit": "H 0\\n..."
            }
        """
        if index < 0 or index >= len(self._index):
            raise IndexError(f"Index {index} out of range [0, {len(self._index)})")
        
        if self.preload:
            return self._data[index]
        else:
            offset = self._index[index][0]
            return self._load_at_offset(offset)
    
    def get_random_prompt(self) -> Dict:
        """
        Sample a random stabilizer prompt.
        
        Returns:
            Prompt dictionary with input_stabilizers, source_code, d, output_circuit
        """
        index = random.randint(0, len(self._index) - 1)
        return self.get_prompt(index)
    
    def get_batch(self, batch_size: int, shuffle: bool = True) -> List[Dict]:
        """
        Get batch of prompts.
        
        Args:
            batch_size: Number of prompts to return
            shuffle: If True, randomly sample; if False, sequential
            
        Returns:
            List of prompt dictionaries
        """
        if shuffle:
            indices = random.sample(range(len(self._index)), min(batch_size, len(self._index)))
        else:
            indices = list(range(min(batch_size, len(self._index))))
        
        return [self.get_prompt(i) for i in indices]
    
    def iterate_prompts(self, shuffle: bool = False) -> Iterator[Dict]:
        """
        Iterate through all prompts.
        
        Args:
            shuffle: If True, iterate in random order
            
        Yields:
            Prompt dictionaries
        """
        indices = list(range(len(self._index)))
        if shuffle:
            random.shuffle(indices)
        
        for idx in indices:
            yield self.get_prompt(idx)
    
    def filter_by_distance(self, min_d: int = None, max_d: int = None) -> List[int]:
        """
        Get indices of prompts within distance range.
        
        Args:
            min_d: Minimum code distance (inclusive)
            max_d: Maximum code distance (inclusive)
            
        Returns:
            List of indices matching criteria
        """
        indices = []
        for i, (_, _, d, _) in enumerate(self._index):
            if (min_d is None or d >= min_d) and (max_d is None or d <= max_d):
                indices.append(i)
        return indices
    
    def filter_by_code(self, source_code: str) -> List[int]:
        """
        Get indices of prompts for a specific error correcting code.
        
        Args:
            source_code: Name of the code (e.g., "Perfect 5-Qubit Code")
            
        Returns:
            List of indices matching the code
        """
        indices = []
        for i, (_, code, _, _) in enumerate(self._index):
            if code == source_code:
                indices.append(i)
        return indices
    
    def filter_by_num_qubits(self, min_qubits: int = None, max_qubits: int = None) -> List[int]:
        """
        Get indices of prompts with qubit count in range.
        
        Args:
            min_qubits: Minimum number of qubits (inclusive)
            max_qubits: Maximum number of qubits (inclusive)
            
        Returns:
            List of indices matching criteria
        """
        indices = []
        for i, (_, _, _, n) in enumerate(self._index):
            if (min_qubits is None or n >= min_qubits) and (max_qubits is None or n <= max_qubits):
                indices.append(i)
        return indices
    
    def get_statistics(self) -> Dict:
        """
        Get dataset statistics.
        
        Returns:
            Dictionary with dataset statistics
        """
        codes = {}
        distances = {}
        qubit_counts = {}
        
        for _, code, d, n in self._index:
            codes[code] = codes.get(code, 0) + 1
            distances[d] = distances.get(d, 0) + 1
            qubit_counts[n] = qubit_counts.get(n, 0) + 1
        
        return {
            'total_examples': len(self._index),
            'unique_codes': len(codes),
            'code_distribution': codes,
            'distance_distribution': distances,
            'qubit_distribution': qubit_counts
        }
    
    def __len__(self) -> int:
        """Return number of prompts in dataset."""
        return len(self._index)
    
    def __getitem__(self, index: int) -> Dict:
        """Allow indexing: loader[42]."""
        return self.get_prompt(index)


class BatchSampler:
    """
    Efficient batch sampler with curriculum learning support.
    """
    
    def __init__(self, loader: PromptLoader, batch_size: int = 32):
        """
        Initialize batch sampler.
        
        Args:
            loader: PromptLoader instance
            batch_size: Default batch size
        """
        self.loader = loader
        self.batch_size = batch_size
        self.epoch = 0
    
    def sample_curriculum(self, difficulty: str = 'mixed') -> List[Dict]:
        """
        Sample batch with curriculum learning.
        
        Args:
            difficulty: 'easy' (small d), 'hard' (large d), or 'mixed'
            
        Returns:
            Batch of prompts
        """
        if difficulty == 'easy':
            indices = self.loader.filter_by_distance(min_d=None, max_d=3)
        elif difficulty == 'hard':
            indices = self.loader.filter_by_distance(min_d=5, max_d=None)
        else:  # mixed
            indices = list(range(len(self.loader)))
        
        if not indices:
            return self.loader.get_batch(self.batch_size)
        
        sampled_indices = random.sample(indices, min(self.batch_size, len(indices)))
        return [self.loader.get_prompt(i) for i in sampled_indices]
    
    def iterate_batches(self, shuffle: bool = True) -> Iterator[List[Dict]]:
        """
        Iterate through dataset in batches.
        
        Args:
            shuffle: If True, shuffle prompts each epoch
            
        Yields:
            Batches of prompts
        """
        indices = list(range(len(self.loader)))
        if shuffle:
            random.shuffle(indices)
        
        for i in range(0, len(indices), self.batch_size):
            batch_indices = indices[i:i + self.batch_size]
            yield [self.loader.get_prompt(idx) for idx in batch_indices]
        
        self.epoch += 1


if __name__ == "__main__":
    # Example usage and testing
    import argparse
    
    parser = argparse.ArgumentParser(description='Test prompt loader')
    parser.add_argument('--jsonl', type=str, default='reinforcement_learning/data/circuit_permute.jsonl',
                        help='Path to JSONL file')
    parser.add_argument('--preload', action='store_true',
                        help='Preload all data into memory')
    parser.add_argument('--test-speed', action='store_true',
                        help='Run speed benchmark')
    
    args = parser.parse_args()
    
    print("="*60)
    print("Initializing PromptLoader...")
    loader = PromptLoader(args.jsonl, preload=args.preload)
    
    stats = loader.get_statistics()
    print(f"\nDataset Statistics:")
    print(f"  Total examples: {stats['total_examples']}")
    print(f"  Unique codes: {stats['unique_codes']}")
    print(f"  Distance distribution: {stats['distance_distribution']}")
    
    print(f"\n{'='*60}")
    print("Testing random sampling...")
    prompt = loader.get_random_prompt()
    print(f"  Source: {prompt['source_code']}")
    print(f"  Distance: {prompt['d']}")
    print(f"  Stabilizers: {prompt['input_stabilizers']}")
    print(f"  Circuit length: {len(prompt['output_circuit'])} chars")
    
    if args.test_speed:
        import time
        
        print(f"\n{'='*60}")
        print("Speed Benchmark:")
        
        # Test random access speed
        start = time.time()
        n_samples = 1000
        for _ in range(n_samples):
            loader.get_random_prompt()
        elapsed = time.time() - start
        
        print(f"  Random sampling: {n_samples} prompts in {elapsed:.3f}s")
        print(f"  Speed: {n_samples/elapsed:.1f} prompts/second")
        
        # Test batch sampling
        start = time.time()
        n_batches = 100
        for _ in range(n_batches):
            loader.get_batch(32)
        elapsed = time.time() - start
        
        print(f"  Batch sampling: {n_batches} batches (32 each) in {elapsed:.3f}s")
        print(f"  Speed: {n_batches*32/elapsed:.1f} prompts/second")
    
    print(f"\n{'='*60}")
    print("✓ PromptLoader working correctly")
