import numpy as np
import pytest
import torch

pytest.importorskip("torch_geometric")

from RL.models.StatePrepGNN import EmbeddingGNN


def _count_nonzero_xz_edges(tableau: np.ndarray) -> int:
    n = tableau.shape[0]
    x = tableau[:, :n]
    z = tableau[:, n : 2 * n]
    return int(np.logical_or(x == 1, z == 1).sum())


def test_graph_construction_counts_and_phase_mapping() -> None:
    # n=2 tableau: columns [X0 X1 Z0 Z1 phase]
    tableau = np.array(
        [
            [1, 0, 0, 1, 0],  # phase bit 0 -> +1
            [0, 1, 1, 0, 1],  # phase bit 1 -> -1
        ],
        dtype=np.int8,
    )

    data = EmbeddingGNN.build_graph(tableau)

    n = 2
    expected_nodes = 2 * n + 1
    assert data.x.shape == (expected_nodes, 2)

    # Stabilizer nodes are indices [n, 2n)
    assert data.x[n, 1].item() == 1.0
    assert data.x[n + 1, 1].item() == -1.0

    nonzero_pairs = _count_nonzero_xz_edges(tableau)
    expected_bipartite_directed = 2 * nonzero_pairs
    expected_virtual_directed = 2 * (2 * n)
    expected_edges = expected_bipartite_directed + expected_virtual_directed

    assert data.edge_index.shape[1] == expected_edges
    assert data.edge_attr.shape == (expected_edges, 2)


def test_forward_single_and_batched_shapes() -> None:
    model = EmbeddingGNN(embedding_dim=32, num_layers=3)

    # Single graph, n=3 -> total nodes 7
    single = np.array(
        [
            [1, 0, 0, 0, 1, 0, 0],
            [0, 1, 0, 1, 0, 0, 1],
            [0, 0, 1, 0, 0, 1, 0],
        ],
        dtype=np.int8,
    )
    single_graph = EmbeddingGNN.build_graph(single)
    out_single = model(single_graph)
    assert out_single.node_embeddings.shape == (7, 32)
    assert out_single.batch_index.shape[0] == 7
    assert out_single.graph_ptr.tolist() == [0, 7]

    # Batch of 2 graphs with same n=3 -> total nodes 14
    batched = np.stack([single, single], axis=0)
    batched_graph = EmbeddingGNN.build_batch_graph(batched)
    out_batch = model(batched_graph)
    assert out_batch.node_embeddings.shape == (14, 32)
    assert out_batch.batch_index.shape[0] == 14
    assert out_batch.graph_ptr.tolist() == [0, 7, 14]


def test_backward_gradient_flow() -> None:
    model = EmbeddingGNN(embedding_dim=8, num_layers=2)

    tableau = np.array(
        [
            [1, 0, 0, 1, 0],
            [0, 1, 1, 0, 1],
        ],
        dtype=np.int8,
    )

    graph = EmbeddingGNN.build_graph(tableau)
    out = model(graph)
    loss = out.node_embeddings.pow(2).mean()
    loss.backward()

    grad_params = [p.grad for p in model.parameters() if p.requires_grad]
    assert any(g is not None for g in grad_params)


def test_build_batch_graph_variable_sized_tableaux() -> None:
    model = EmbeddingGNN(embedding_dim=16, num_layers=2)

    t2 = np.array(
        [
            [1, 0, 0, 1, 0],
            [0, 1, 1, 0, 1],
        ],
        dtype=np.int8,
    )
    t3 = np.array(
        [
            [1, 0, 0, 0, 1, 0, 0],
            [0, 1, 0, 1, 0, 0, 1],
            [0, 0, 1, 0, 0, 1, 0],
        ],
        dtype=np.int8,
    )

    batch_graph = EmbeddingGNN.build_batch_graph([t2, t3])
    out = model(batch_graph)

    # Nodes per graph are (2n + 1): n=2 -> 5, n=3 -> 7
    assert out.graph_ptr.tolist() == [0, 5, 12]
    assert out.node_embeddings.shape == (12, 16)
    assert int((out.batch_index == 0).sum().item()) == 5
    assert int((out.batch_index == 1).sum().item()) == 7

    split_a = out.split_embeddings()
    split_b = EmbeddingGNN.split_embeddings(out)

    assert len(split_a) == 2
    assert split_a[0].shape == (5, 16)
    assert split_a[1].shape == (7, 16)
    assert torch.allclose(split_a[0], split_b[0])
    assert torch.allclose(split_a[1], split_b[1])
