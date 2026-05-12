from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import importlib
from typing import Any, Sequence

import numpy as np
import torch
from torch import Tensor, nn


@lru_cache(maxsize=1)
def _get_pyg_classes() -> tuple[Any, Any, Any]:
	"""Load PyG classes lazily and raise a clear install error if missing."""
	try:
		pyg_data = importlib.import_module("torch_geometric.data")
		pyg_nn = importlib.import_module("torch_geometric.nn")
	except ImportError as exc:
		raise ImportError(
			"torch-geometric is required for EmbeddingGNN. "
			"Install dependencies from RL/requirements.txt."
		) from exc
	return pyg_data.Data, pyg_data.Batch, pyg_nn.GINEConv


@dataclass(frozen=True)
class EmbeddingGNNOutput:
	"""Container for node embeddings and graph-membership metadata."""

	node_embeddings: Tensor
	batch_index: Tensor
	graph_ptr: Tensor

	def split_embeddings(self) -> list[Tensor]:
		"""Split node embeddings into one tensor per connected component/graph."""
		if self.graph_ptr.ndim != 1:
			raise ValueError("graph_ptr must be a 1D tensor")
		if self.graph_ptr.numel() < 2:
			return [self.node_embeddings]

		splits: list[Tensor] = []
		for i in range(self.graph_ptr.numel() - 1):
			start = int(self.graph_ptr[i].item())
			end = int(self.graph_ptr[i + 1].item())
			splits.append(self.node_embeddings[start:end])
		return splits


@dataclass(frozen=True)
class StatePrepAlphaZeroOutput:
	"""Combined outputs from embedding trunk, policy head, and value head."""

	embeddings: EmbeddingGNNOutput
	policy_probs: list[Tensor]
	values: Tensor


class EmbeddingGNN(nn.Module):
	"""Edge-aware embedding GNN for stabilizer-tableau graphs.

	Graph construction for a tableau of shape (n, 2n+1):
	- Qubit nodes: n nodes with feature [1, 0]
	- Stabilizer nodes: n nodes with feature [0, phase_sign]
	  where phase_sign is +1 if phase bit is 0 else -1
	- Virtual node: 1 node with feature [0, 0], connected to all non-virtual nodes
	- Bipartite edges: between stabilizer j and qubit i with edge_attr [X_ji, Z_ji]
	  only when at least one of X_ji or Z_ji equals 1
	- All edges are bidirectional
	"""

	def __init__(
		self,
		embedding_dim: int,
		num_layers: int = 3,
		dropout: float = 0.0,
	) -> None:
		super().__init__()
		_, _, gine_conv_cls = _get_pyg_classes()

		if embedding_dim <= 0:
			raise ValueError("embedding_dim must be > 0")
		if num_layers <= 0:
			raise ValueError("num_layers must be > 0")

		self.embedding_dim = embedding_dim
		self.num_layers = num_layers
		self.dropout = nn.Dropout(dropout)

		self.input_proj = nn.Linear(2, embedding_dim)
		self.convs = nn.ModuleList()
		self.norms = nn.ModuleList()

		for _ in range(num_layers):
			mlp = nn.Sequential(
				nn.Linear(embedding_dim, embedding_dim),
				nn.ReLU(),
				nn.Linear(embedding_dim, embedding_dim),
			)
			self.convs.append(gine_conv_cls(nn=mlp, edge_dim=2, train_eps=True))
			self.norms.append(nn.LayerNorm(embedding_dim))

	def forward(self, graph: Any) -> EmbeddingGNNOutput:
		"""Return node embeddings for a pre-built PyG Data/Batch graph.

		Input:
		- graph: torch_geometric.data.Data or torch_geometric.data.Batch
		  with x, edge_index, edge_attr and (for Data) optional batch/ptr.

		Output:
		- node_embeddings: (total_nodes_across_batch, embedding_dim)
		- batch_index: graph id for each node (same length as total_nodes)
		- graph_ptr: cumulative node offsets per graph (length B+1)
		"""
		_, _, _ = _get_pyg_classes()

		required = ("x", "edge_index", "edge_attr")
		for attr in required:
			if not hasattr(graph, attr):
				raise ValueError(f"graph is missing required attribute '{attr}'")

		# Keep graph tensors on the same device as model parameters.
		model_device = self.input_proj.weight.device
		if hasattr(graph, "to"):
			graph = graph.to(model_device)

		x = self.input_proj(graph.x)

		for conv, norm in zip(self.convs, self.norms):
			msg = conv(x, graph.edge_index, graph.edge_attr)
			x = norm(x + self.dropout(msg))

		if hasattr(graph, "batch") and graph.batch is not None:
			batch_index = graph.batch
		else:
			batch_index = torch.zeros(x.size(0), dtype=torch.long, device=x.device)

		if hasattr(graph, "ptr") and graph.ptr is not None:
			graph_ptr = graph.ptr
		else:
			graph_ptr = torch.tensor([0, x.size(0)], dtype=torch.long, device=x.device)

		return EmbeddingGNNOutput(
			node_embeddings=x,
			batch_index=batch_index,
			graph_ptr=graph_ptr,
		)

	@staticmethod
	def split_embeddings(output: EmbeddingGNNOutput) -> list[Tensor]:
		"""Convenience wrapper for splitting output embeddings by component."""
		return output.split_embeddings()

	@staticmethod
	def build_graph(
		tableau: np.ndarray | Tensor,
		virtual_node_feature: Sequence[float] = (0.0, 0.0),
	) -> Any:
		"""Build a single PyG Data graph from one tableau of shape (n, 2n+1)."""
		if len(virtual_node_feature) != 2:
			raise ValueError("virtual_node_feature must have length 2")

		data_cls, _, _ = _get_pyg_classes()
		t = EmbeddingGNN._to_tableau_tensor(tableau)
		if t.ndim != 2:
			raise ValueError(f"single tableau must be 2D, got {t.ndim}D")

		n = t.shape[0]
		expected_cols = 2 * n + 1
		if t.shape[1] != expected_cols:
			raise ValueError(f"expected tableau shape (n, 2n+1); got ({n}, {t.shape[1]})")

		x_part = t[:, :n].to(torch.int64)
		z_part = t[:, n : 2 * n].to(torch.int64)
		phase = t[:, 2 * n].to(torch.int64)

		qubit_features = torch.tensor([[1.0, 0.0]], dtype=torch.float32).repeat(n, 1)
		phase_sign = torch.where(phase == 0, 1.0, -1.0).to(torch.float32)
		stabilizer_features = torch.stack([torch.zeros_like(phase_sign), phase_sign], dim=1)
		virtual_feature = torch.tensor(virtual_node_feature, dtype=torch.float32).unsqueeze(0)
		# Node order is [qubits][stabilizers][virtual], so qubit embeddings are always [:n].
		node_features = torch.cat([qubit_features, stabilizer_features, virtual_feature], dim=0)

		src_nodes: list[int] = []
		dst_nodes: list[int] = []
		edge_attrs: list[list[float]] = []

		for j in range(n):
			stabilizer_idx = n + j
			for i in range(n):
				x_ji = int(x_part[j, i].item())
				z_ji = int(z_part[j, i].item())
				if x_ji == 0 and z_ji == 0:
					continue
				qubit_idx = i
				attr = [float(x_ji), float(z_ji)]
				src_nodes.extend([stabilizer_idx, qubit_idx])
				dst_nodes.extend([qubit_idx, stabilizer_idx])
				edge_attrs.extend([attr, attr])

		virtual_idx = 2 * n
		for node_idx in range(2 * n):
			src_nodes.extend([virtual_idx, node_idx])
			dst_nodes.extend([node_idx, virtual_idx])
			edge_attrs.extend([[0.0, 0.0], [0.0, 0.0]])

		if src_nodes:
			edge_index = torch.tensor([src_nodes, dst_nodes], dtype=torch.long)
			edge_attr = torch.tensor(edge_attrs, dtype=torch.float32)
		else:
			edge_index = torch.zeros((2, 0), dtype=torch.long)
			edge_attr = torch.zeros((0, 2), dtype=torch.float32)

		return data_cls(
			x=node_features,
			edge_index=edge_index,
			edge_attr=edge_attr,
			num_qubits=n,
			num_stabilizers=n,
			virtual_node_idx=virtual_idx,
		)

	@staticmethod
	def build_batch_graph(
		tableaux: Sequence[np.ndarray | Tensor] | np.ndarray | Tensor,
		virtual_node_feature: Sequence[float] = (0.0, 0.0),
	) -> Any:
		"""Build a batched PyG Batch graph from tableaux.

		Accepted shapes:
		- (n, 2n+1): returns batch with one graph
		- (B, n, 2n+1): returns batch with B graphs
		- Sequence of tableaux with potentially different n values
		  (returns one disconnected graph component per tableau)
		"""
		_, batch_cls, _ = _get_pyg_classes()

		if isinstance(tableaux, (list, tuple)):
			if len(tableaux) == 0:
				raise ValueError("tableaux sequence must not be empty")
			data_list = [
				EmbeddingGNN.build_graph(t, virtual_node_feature=virtual_node_feature)
				for t in tableaux
			]
		else:
			if not isinstance(tableaux, (np.ndarray, Tensor)):
				raise TypeError(f"Unsupported tableaux type: {type(tableaux)!r}")
			t = EmbeddingGNN._to_tableau_tensor(tableaux)
			if t.ndim == 2:
				data_list = [EmbeddingGNN.build_graph(t, virtual_node_feature=virtual_node_feature)]
			elif t.ndim == 3:
				data_list = [
					EmbeddingGNN.build_graph(t[i], virtual_node_feature=virtual_node_feature)
					for i in range(t.shape[0])
				]
			else:
				raise ValueError(
					"tableaux must be a sequence of 2D tableaux or have shape "
					f"(n, 2n+1)/(B, n, 2n+1), got {tuple(t.shape)}"
				)

		return batch_cls.from_data_list(data_list)

	@staticmethod
	def _to_tableau_tensor(tableau: np.ndarray | Tensor) -> Tensor:
		if isinstance(tableau, np.ndarray):
			tensor = torch.from_numpy(tableau)
		elif isinstance(tableau, Tensor):
			tensor = tableau
		else:
			raise TypeError(f"Unsupported tableau type: {type(tableau)!r}")
		return tensor.to(torch.float32)


class StatePrepActionHead(nn.Module):
	"""AlphaZero-style policy head for state-preparation actions."""

	def __init__(
		self,
		embedding_dim: int,
		num_one_qubit_gates: int,
		num_two_qubit_gates: int,
		hidden_dim: int | None = None,
	) -> None:
		super().__init__()
		if embedding_dim <= 0:
			raise ValueError("embedding_dim must be > 0")
		if num_one_qubit_gates <= 0:
			raise ValueError("num_one_qubit_gates must be > 0")
		if num_two_qubit_gates <= 0:
			raise ValueError("num_two_qubit_gates must be > 0")

		h = hidden_dim or embedding_dim
		self.num_one_qubit_gates = num_one_qubit_gates
		self.num_two_qubit_gates = num_two_qubit_gates

		self.one_qubit_mlp = nn.Sequential(
			nn.Linear(embedding_dim, h),
			nn.ReLU(),
			nn.Linear(h, num_one_qubit_gates),
		)
		self.two_qubit_mlp = nn.Sequential(
			nn.Linear(2 * embedding_dim, h),
			nn.ReLU(),
			nn.Linear(h, num_two_qubit_gates),
		)

	def forward(self, qubit_embeddings: Tensor | list[Tensor]) -> list[Tensor]:
		components = (
			[qubit_embeddings]
			if isinstance(qubit_embeddings, Tensor)
			else qubit_embeddings
		)

		policy_probs: list[Tensor] = []
		head_device = next(self.parameters()).device

		for q_emb in components:
			q_emb = q_emb.to(head_device)
			logits = self._forward_single(q_emb)
			probs = torch.softmax(logits, dim=0)
			policy_probs.append(probs)

		return policy_probs

	def _forward_single(self, qubit_embeddings: Tensor) -> Tensor:
		if qubit_embeddings.ndim != 2:
			raise ValueError(
				f"Expected qubit embeddings shape (n, d), got {tuple(qubit_embeddings.shape)}"
			)

		n = qubit_embeddings.shape[0]
		if n < 1:
			raise ValueError("At least 1 qubit embedding is required.")

		# Single-qubit branch: row-major flatten gives qubit-major ordering.
		single_scores = self.one_qubit_mlp(qubit_embeddings)
		single_flat = single_scores.reshape(-1)

		# Two-qubit branch over ordered pairs with control != target.
		if n == 1:
			two_flat = torch.empty(0, dtype=single_flat.dtype, device=single_flat.device)
		else:
			pair_control, pair_target = self._ordered_pairs(n, qubit_embeddings.device)
			control_emb = qubit_embeddings.index_select(0, pair_control)
			target_emb = qubit_embeddings.index_select(0, pair_target)
			pair_emb = torch.cat([control_emb, target_emb], dim=1)
			two_scores = self.two_qubit_mlp(pair_emb)
			two_flat = two_scores.reshape(-1)

		return torch.cat([single_flat, two_flat], dim=0)

	@staticmethod
	def _ordered_pairs(n: int, device: torch.device) -> tuple[Tensor, Tensor]:
		"""Return control/target index tensors in env-compatible pair order."""
		controls: list[int] = []
		targets: list[int] = []
		for control in range(n):
			for target in range(n):
				if control == target:
					continue
				controls.append(control)
				targets.append(target)
		return (
			torch.tensor(controls, dtype=torch.long, device=device),
			torch.tensor(targets, dtype=torch.long, device=device),
		)


class StatePrepValueHead(nn.Module):
	"""AlphaZero-style value head over component-level pooled embeddings."""

	def __init__(
		self,
		embedding_dim: int,
		hidden_dim: int | None = None,
	) -> None:
		super().__init__()
		if embedding_dim <= 0:
			raise ValueError("embedding_dim must be > 0")

		h = hidden_dim or embedding_dim
		self.mlp = nn.Sequential(
			nn.Linear(embedding_dim, h),
			nn.ReLU(),
			nn.Linear(h, 1),
		)

	def forward(self, component_embeddings: Tensor | list[Tensor]) -> Tensor:
		components = (
			[component_embeddings]
			if isinstance(component_embeddings, Tensor)
			else component_embeddings
		)

		values: list[Tensor] = []
		head_device = next(self.parameters()).device
		for emb in components:
			emb = emb.to(head_device)
			if emb.ndim != 2:
				raise ValueError(
					f"Expected component embeddings shape (num_nodes, d), got {tuple(emb.shape)}"
				)
			pooled = emb.mean(dim=0)
			value = torch.sigmoid(self.mlp(pooled)).squeeze(-1)
			values.append(value)

		if not values:
			return torch.empty(0)
		return torch.stack(values, dim=0)


class StatePrepAlphaZeroModel(nn.Module):
	"""Composite model: EmbeddingGNN trunk + AlphaZero policy and value heads."""

	def __init__(
		self,
		embedding_gnn: EmbeddingGNN,
		action_head: StatePrepActionHead,
		value_head: StatePrepValueHead,
	) -> None:
		super().__init__()
		self.embedding_gnn = embedding_gnn
		self.action_head = action_head
		self.value_head = value_head

	def forward(self, graph: Any) -> StatePrepAlphaZeroOutput:
		embedding_output = self.embedding_gnn(graph)
		components = embedding_output.split_embeddings()
		qubit_components = [self._extract_qubit_nodes(c) for c in components]

		policy_probs = self.action_head(qubit_components)
		values = self.value_head(components)

		return StatePrepAlphaZeroOutput(
			embeddings=embedding_output,
			policy_probs=policy_probs,
			values=values,
		)

	@staticmethod
	def _extract_qubit_nodes(component_embeddings: Tensor) -> Tensor:
		if component_embeddings.ndim != 2:
			raise ValueError(
				"Expected component embeddings shape (2n+1, d) for qubit extraction."
			)
		nodes = component_embeddings.shape[0]
		if nodes < 3 or nodes % 2 == 0:
			raise ValueError(
				f"Invalid component node count {nodes}; expected odd value (2n+1)."
			)
		n = (nodes - 1) // 2
		return component_embeddings[:n]

