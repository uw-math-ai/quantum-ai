import unittest

import stim

from tools.check_error_propagation import (
    check_error_propagation,
    ft_score,
    parse_circuit_to_gate_list,
    propagate_fault,
)


class CheckErrorPropagationTests(unittest.TestCase):
    def assert_same_faults(self, left, right, data=(0, 1, 2), flags=()):
        self.assertEqual(
            check_error_propagation(left, list(data), list(flags)),
            check_error_propagation(right, list(data), list(flags)),
        )

    def test_nested_repeats_match_unrolled_circuit(self):
        self.assert_same_faults(
            "H 0\nREPEAT 2 {\nCX 0 1\nREPEAT 2 {\nH 1\n}\n}",
            "H 0\nCX 0 1\nH 1\nH 1\nCX 0 1\nH 1\nH 1",
        )

    def test_packed_swaps_match_separate_operations(self):
        self.assert_same_faults("SWAP 0 1 1 2", "SWAP 0 1\nTICK\nSWAP 1 2")

    def test_packed_single_qubit_cliffords_match_separate_operations(self):
        self.assert_same_faults("H_XY 0 1\nCX 0 1", "H_XY 0\nTICK\nH_XY 1\nCX 0 1")

    def test_annotations_do_not_create_fault_sites(self):
        self.assert_same_faults(
            "QUBIT_COORDS(1, 2) 0\nH 0\nCX 0 1\nTICK\nM 2\n"
            "DETECTOR rec[-1]\nSHIFT_COORDS(0, 1)\nOBSERVABLE_INCLUDE(0) rec[-1]",
            "H 0\nCX 0 1\nM 2",
        )

    def test_fault_between_packed_pairs_can_spread(self):
        circuit = "SQRT_XX 0 1 1 2"
        rows = check_error_propagation(circuit, [0, 1, 2], [])
        fault = next(r for r in rows if r["loc"] == 0 and r["fault_qubit"] == 1 and r["fault_pauli"] == "Z")
        self.assertEqual(fault["final_paulis"], {0: "I", 1: "Y", 2: "X"})
        self.assertEqual(fault["data_weight"], 2)
        self.assertEqual(ft_score(circuit, [0, 1, 2], [], d=3), 0.0)

    def test_packed_reset_prefix_reports_all_fault_sites(self):
        circuit = "R 0 1\nH 0\nCX 0 1"
        rows = check_error_propagation(circuit, [0, 1], [])
        self.assertEqual(len(rows), 15)
        self.assertEqual(
            sorted({(r["loc"], r["gate"], r["fault_qubit"]) for r in rows}),
            [(0, "R", 0), (1, "R", 1), (2, "H", 0), (3, "CX", 0), (3, "CX", 1)],
        )
        after_r0 = {r["fault_pauli"]: r for r in rows if r["loc"] == 0}
        self.assertEqual(after_r0["X"]["final_paulis"], {0: "Z", 1: "I"})
        self.assertEqual(after_r0["Z"]["final_paulis"], {0: "X", 1: "X"})
        self.assertEqual(after_r0["Z"]["data_weight"], 2)
        self.assertEqual(ft_score(circuit, [0, 1], [], d=3), 0.0)

    def test_reset_erases_earlier_fault(self):
        rows = check_error_propagation("H 0\nR 0", [0], [])
        for r in rows[:3]:
            self.assertEqual(r["final_paulis"], {0: "I"})
            self.assertEqual(r["data_weight"], 0)
        self.assertEqual(rows[3]["final_paulis"], {0: "X"})
        self.assertEqual(ft_score("H 0\nR 0", [0], [], d=3), 1.0)

    def test_entangling_propagation_around_reset(self):
        gate_list = parse_circuit_to_gate_list(stim.Circuit("H 0\nCX 0 1\nR 1\nCX 1 2"))

        paulis, _, _ = propagate_fault(gate_list, 0, "X", 0)
        self.assertEqual(paulis, {0: "X", 1: "I", 2: "I"})
        paulis, _, _ = propagate_fault(gate_list, 1, "X", 1)
        self.assertEqual(paulis, {0: "I", 1: "I", 2: "I"})
        paulis, x_mask, _ = propagate_fault(gate_list, 2, "X", 1)
        self.assertEqual(paulis, {0: "I", 1: "X", 2: "X"})
        self.assertEqual(x_mask, {1, 2})

    def test_reset_basis_and_measurement_reset_variants(self):
        for gate in ("R", "RX", "RY", "MR", "MRX", "MRY"):
            with self.subTest(gate=gate):
                gate_list = parse_circuit_to_gate_list(stim.Circuit(f"S 0\n{gate} 0\nH 0"))
                for pauli in ("X", "Z", "Y"):
                    paulis, _, _ = propagate_fault(gate_list, 0, pauli, 0)
                    self.assertEqual(paulis, {0: "I"})

    def test_packed_resets_match_separate_operations(self):
        self.assert_same_faults(
            "R 0 1\nH 0\nCX 0 1", "R 0\nTICK\nR 1\nH 0\nCX 0 1", data=(0, 1)
        )

if __name__ == "__main__":
    unittest.main()
