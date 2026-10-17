import unittest

from tools.circuit_metric import compute_metrics, is_strictly_more_optimal


class CircuitMetricTests(unittest.TestCase):
    def test_fixed_arity_two_qubit_gates(self):
        for gate in ("CX", "CY", "CZ", "SWAP", "ISWAP", "SQRT_XX", "SQRT_YY", "SQRT_ZZ"):
            with self.subTest(gate=gate):
                metrics = compute_metrics(f"{gate} 0 1 2 3")
                self.assertEqual(metrics.two_qubit_gates, 2)
                self.assertEqual(metrics.one_qubit_gates, 0)
                self.assertEqual(metrics.depth, 1)

    def test_two_qubit_depth_tracks_both_targets(self):
        metrics = compute_metrics("H 0\nCY 0 1\nCY 1 2")
        self.assertEqual(metrics.two_qubit_gates, 2)
        self.assertEqual(metrics.one_qubit_gates, 1)
        self.assertEqual(metrics.depth, 3)

    def test_repeated_packed_gates(self):
        metrics = compute_metrics("REPEAT 2 {\nREPEAT 3 {\nCY 0 1 2 3\n}\n}")
        self.assertEqual(metrics.two_qubit_gates, 12)
        self.assertEqual(metrics.depth, 6)

    def test_extra_cy_gates_are_not_an_improvement(self):
        better, _ = is_strictly_more_optimal("CY 0 1 0 1 0 1 0 1", "CX 0 1 0 1")
        self.assertFalse(better)

    def test_feedback_pairs_are_one_qubit(self):
        for gate, targets in (("CY", "rec[-1] 1"), ("CZ", "1 rec[-1]")):
            with self.subTest(gate=gate, targets=targets):
                metrics = compute_metrics(f"M 0\n{gate} {targets}", volume_gates=frozenset({gate}))
                self.assertEqual(metrics.two_qubit_gates, 0)
                self.assertEqual(metrics.one_qubit_gates, 2)
                self.assertEqual(metrics.volume, 1)

    def test_packed_feedback_operations(self):
        metrics = compute_metrics("M 0 1\nCX rec[-1] 0 rec[-2] 2", volume_gates=frozenset({"CX"}))
        self.assertEqual(metrics.two_qubit_gates, 0)
        self.assertEqual(metrics.one_qubit_gates, 4)
        self.assertEqual(metrics.volume, 2)
        self.assertEqual(metrics.depth, 2)

    def test_sweep_controlled_operation_and_quantum_pair(self):
        metrics = compute_metrics("CX sweep[0] 3 4 5", volume_gates=frozenset({"CX"}))
        self.assertEqual(metrics.one_qubit_gates, 1)
        self.assertEqual(metrics.two_qubit_gates, 1)
        self.assertEqual(metrics.volume, 2)

    def test_feedback_does_not_pair_with_following_quantum_pair(self):
        metrics = compute_metrics("M 0\nCY rec[-1] 1 2 3", volume_gates=frozenset({"CY"}))
        self.assertEqual(metrics.two_qubit_gates, 1)
        self.assertEqual(metrics.one_qubit_gates, 2)
        self.assertEqual(metrics.volume, 2)


if __name__ == "__main__":
    unittest.main()
