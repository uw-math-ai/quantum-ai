import unittest

from tools.check_stabilizers import check_stabilizers


class CheckStabilizersTests(unittest.TestCase):
    def test_random_measurement_does_not_prepare_either_sign(self):
        for circuit, pauli in (("H 0\nM 0", "Z"), ("MX 0", "X"), ("MY 0", "Y")):
            with self.subTest(circuit=circuit):
                self.assertEqual(
                    check_stabilizers(circuit, [pauli, "-" + pauli]),
                    {pauli: False, "-" + pauli: False},
                )

    def test_reset_does_not_preserve_a_sampled_entangled_partner(self):
        self.assertEqual(
            check_stabilizers("H 0\nCX 0 1\nR 0", ["IZ", "-IZ"]),
            {"IZ": False, "-IZ": False},
        )

    def test_unrelated_ancilla_measurement_is_allowed(self):
        self.assertEqual(
            check_stabilizers("H 0\nCX 0 1\nH 2\nM 2", ["XX", "ZZ", "-XX"]),
            {"XX": True, "ZZ": True, "-XX": False},
        )

    def test_feedforward_can_restore_a_deterministic_state(self):
        self.assertEqual(check_stabilizers("H 0\nM 0\nCX rec[-1] 0", ["Z"]), {"Z": True})

    def test_repeated_measurements_are_branch_independent(self):
        self.assertEqual(
            check_stabilizers("REPEAT 2 {\nH 0\nM 0\n}", ["Z", "-Z"]),
            {"Z": False, "-Z": False},
        )

    def test_initial_state_and_sign_are_retained(self):
        self.assertEqual(check_stabilizers("", ["ZZ"]), {"ZZ": True})
        self.assertEqual(check_stabilizers("X 0", ["Z", "-Z"]), {"Z": False, "-Z": True})


if __name__ == "__main__":
    unittest.main()
