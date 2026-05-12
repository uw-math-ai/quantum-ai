import numpy as np
import pytest
import torch

pytest.importorskip("torch_geometric")

from RL.models.StatePrepGNN import (
    EmbeddingGNN,
    StatePrepActionHead,
    StatePrepValueHead,
    StatePrepAlphaZeroModel,
)


def _sample_tableau(n: int) -> np.ndarray:
    # Simple valid-shape binary tableau (not necessarily physically canonical).
    x = np.eye(n, dtype=np.int8)
    z = np.roll(np.eye(n, dtype=np.int8), shift=1, axis=1)
    phase = np.zeros((n, 1), dtype=np.int8)
    return np.concatenate([x, z, phase], axis=1)


def test_action_head_output_shape_and_softmax() -> None:
    d = 16
    g1 = 5
    g2 = 1
    n = 3

    head = StatePrepActionHead(
        embedding_dim=d,
        num_one_qubit_gates=g1,
        num_two_qubit_gates=g2,
    )

    qubit_emb = torch.randn(n, d)
    out = head(qubit_emb)

    assert len(out) == 1

    expected_len = n * g1 + n * (n - 1) * g2
    assert out[0].shape == (expected_len,)
    assert torch.isclose(out[0].sum(), torch.tensor(1.0), atol=1e-6)


def test_value_head_output_range() -> None:
    d = 12
    head = StatePrepValueHead(embedding_dim=d)

    comp_a = torch.randn(5, d)
    comp_b = torch.randn(7, d)
    values = head([comp_a, comp_b])

    assert values.shape == (2,)
    assert torch.all(values >= 0.0)
    assert torch.all(values <= 1.0)


def test_alphazero_wrapper_variable_sized_batch() -> None:
    d = 32
    g1 = 5
    g2 = 1

    gnn = EmbeddingGNN(embedding_dim=d, num_layers=2)
    action_head = StatePrepActionHead(
        embedding_dim=d,
        num_one_qubit_gates=g1,
        num_two_qubit_gates=g2,
    )
    value_head = StatePrepValueHead(embedding_dim=d)
    model = StatePrepAlphaZeroModel(gnn, action_head, value_head)

    t2 = _sample_tableau(2)
    t3 = _sample_tableau(3)
    graph = EmbeddingGNN.build_batch_graph([t2, t3])

    out = model(graph)

    assert len(out.policy_probs) == 2
    assert out.values.shape == (2,)

    # Policy vector lengths: n*g1 + n*(n-1)*g2
    assert out.policy_probs[0].shape == (2 * g1 + 2 * 1 * g2,)
    assert out.policy_probs[1].shape == (3 * g1 + 3 * 2 * g2,)

    assert torch.isclose(out.policy_probs[0].sum(), torch.tensor(1.0), atol=1e-6)
    assert torch.isclose(out.policy_probs[1].sum(), torch.tensor(1.0), atol=1e-6)


def test_alphazero_end_to_end_gradient_flow() -> None:
    d = 16
    g1 = 5
    g2 = 1

    gnn = EmbeddingGNN(embedding_dim=d, num_layers=2)
    action_head = StatePrepActionHead(
        embedding_dim=d,
        num_one_qubit_gates=g1,
        num_two_qubit_gates=g2,
    )
    value_head = StatePrepValueHead(embedding_dim=d)
    model = StatePrepAlphaZeroModel(gnn, action_head, value_head)

    graph = EmbeddingGNN.build_graph(_sample_tableau(3))
    out = model(graph)

    # Use probs + value to ensure gradients flow through all modules.
    loss = out.policy_probs[0].pow(2).mean() + out.values.mean()
    loss.backward()

    grads = [p.grad for p in model.parameters() if p.requires_grad]
    assert any(g is not None for g in grads)


def test_action_head_supports_single_qubit() -> None:
    d = 16
    g1 = 5
    g2 = 1

    head = StatePrepActionHead(
        embedding_dim=d,
        num_one_qubit_gates=g1,
        num_two_qubit_gates=g2,
    )

    qubit_emb = torch.randn(1, d)
    out = head(qubit_emb)

    # For n=1, there are no two-qubit actions; output should be only one-qubit logits.
    assert len(out) == 1
    assert out[0].shape == (g1,)
    assert torch.isclose(out[0].sum(), torch.tensor(1.0), atol=1e-6)


def test_alphazero_wrapper_supports_single_qubit_graph() -> None:
    d = 16
    g1 = 5
    g2 = 1

    gnn = EmbeddingGNN(embedding_dim=d, num_layers=2)
    action_head = StatePrepActionHead(
        embedding_dim=d,
        num_one_qubit_gates=g1,
        num_two_qubit_gates=g2,
    )
    value_head = StatePrepValueHead(embedding_dim=d)
    model = StatePrepAlphaZeroModel(gnn, action_head, value_head)

    # n=1 tableau shape is (1, 3): [X0, Z0, phase]
    t1 = np.array([[0, 1, 0]], dtype=np.int8)
    graph = EmbeddingGNN.build_graph(t1)
    out = model(graph)

    assert len(out.policy_probs) == 1
    assert out.policy_probs[0].shape == (g1,)
    assert out.values.shape == (1,)
