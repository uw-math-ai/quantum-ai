import unittest

from tools.check_error_propagation import check_error_propagation


class FaultSuffixTests(unittest.TestCase):
    def test_fault_is_injected_after_its_gate(self):
        rows = check_error_propagation("H 0\nCX 0 1\nS 1\nM 1", [0], [1])
        self.assertEqual(rows[0], {
            "loc": 0, "gate": "H", "fault_qubit": 0, "fault_pauli": "X",
            "final_paulis": {0: "X", 1: "Y"}, "data_weight": 1, "flag_weight": 1,
        })

    def test_last_gate_has_identity_suffix(self):
        rows = check_error_propagation("H 0", [0], [])
        self.assertEqual([r["final_paulis"] for r in rows], [{0: "X"}, {0: "Z"}, {0: "Y"}])

    def test_suffix_retains_full_circuit_width(self):
        rows = check_error_propagation("I 7\nH 0\nCX 0 1", [0, 1], [])
        self.assertEqual(rows[-1]["final_paulis"], {0: "I", 1: "Y", 2: "I", 3: "I", 4: "I", 5: "I", 6: "I", 7: "I"})

    def test_grouped_packed_operations_keep_their_order(self):
        rows = check_error_propagation("H 0\nSWAP 0 1 1 2", [0, 1, 2], [])
        self.assertEqual(rows[0]["final_paulis"], {0: "I", 1: "I", 2: "X"})

    def test_measurements_in_suffix_are_ignored(self):
        rows = check_error_propagation("H 0\nM 0\nS 0", [0], [])
        self.assertEqual(rows[0]["final_paulis"], {0: "Y"})

    def test_reset_before_first_data_fault_is_not_propagated(self):
        rows = check_error_propagation("I 2\nR 2\nH 0", [0], [2])
        self.assertEqual([r["loc"] for r in rows], [2, 2, 2])
        self.assertEqual([r["final_paulis"] for r in rows], [
            {0: "X", 1: "I", 2: "I"},
            {0: "Z", 1: "I", 2: "I"},
            {0: "Y", 1: "I", 2: "I"},
        ])

    def test_no_data_faults_do_not_require_a_suffix(self):
        self.assertEqual(check_error_propagation("R 0\nR 0", [], [0]), [])
        self.assertEqual(check_error_propagation("", [0], []), [])

    def test_reset_in_fault_suffix_remains_unsupported(self):
        with self.assertRaises(ValueError):
            check_error_propagation("H 0\nR 0", [0], [])


if __name__ == "__main__":
    unittest.main()
