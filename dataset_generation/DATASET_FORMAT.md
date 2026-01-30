# Dataset Format

Each line in the JSONL file is a JSON object with this structure:

```json
{
  "source_code": "Perfect 5-Qubit Code",
  "d": 3,
  "permutation": [0, 1, 2, 3, 4],
  "input_stabilizers": ["XZZXI", "IXZZX", "XIXZZ", "ZXIXZ"],
  "output_circuit": "H 0\\nCX 0 1\\nCX 1 2\\n..."
}
```

## Reading the circuit

```python
import json

with open('circuit_dataset.jsonl', 'r') as f:
    for line in f:
        entry = json.loads(line)
        circuit_str = entry['output_circuit'].replace('\\n', '\n')
        print(circuit_str)
```
