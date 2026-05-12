# Single-Player AlphaZero (PyTorch) for Gym: Minimal Design

This is a deliberately simple design for a single-player AlphaZero-style agent.
It is inspired by the "for dummies" spirit: keep only what is required to work.

## 1. Goal

Train an agent for a single-player Gym/Gymnasium environment with:

- MCTS for planning.
- One PyTorch network with two heads:
  - policy logits over discrete actions
  - value estimate for expected return
- CUDA training on any available number of GPUs.
- Parallel tree search on any configured number of CPU workers.

No advanced features in v1.

## 2. Assumptions (Keep It Simple)

- Environment uses Discrete action space.
- Environment follows Gym API:
  - reset(seed=None) -> (obs, info)
  - step(action) -> (obs, reward, terminated, truncated, info)
- No action masking.
- CPU workers can run in parallel, each with its own env instance.
- GPU count is configurable (1..N), including single-GPU and multi-GPU.

If an environment does not satisfy these, wrap it before using this design.

## 3. Core Idea

At each state:

1. Run MCTS from current root state.
2. Convert root visit counts to a probability target pi.
3. Pick action from pi (sample in training, argmax in evaluation).
4. Store (obs, pi) in trajectory.
5. After episode ends, compute return z for each step.
6. Train network on (obs, pi, z).

The network improves MCTS, and MCTS generates stronger policy targets for the network.

## 4. Math (Only What We Need)

Objective:

J(pi) = E[ sum_t gamma^t r_t ]

PUCT score used during tree selection:

UCB(s,a) = Q(s,a) + c_puct * P(s,a) * sqrt(sum_b N(s,b)) / (1 + N(s,a))

Backup rule in single-player setting:

v_parent = r + gamma * v_child

Policy target from root visits:

pi(a|s) = N(s,a)^(1/tau) / sum_b N(s,b)^(1/tau)

Value target (Monte Carlo return):

z_t = sum_{k=t}^{T-1} gamma^(k-t) r_k

Training loss:

L = CE(pi_target, policy_logits) + lambda_v * MSE(z, value_pred)

## 5. Minimal Components

## 5.1 Model Interface (Model-Agnostic)

MCTS must not depend on a specific model class (including StatePrepGNN).

MCTS only needs this normalized output at a root/leaf state:

- priors: shape (A,), probabilities over discrete actions
- value: scalar float

To keep this generic, use a thin model adapter between MCTS and any PyTorch model.

Adapter contract:

- input: observation from env (any type)
- output: (priors, value)

This allows plugging in:

- simple tensor models that return (policy_logits, value), and
- existing RL/models wrappers that return richer objects (for example policy lists + values).

MCTS never reads internal model fields; it only consumes adapter output.

## 5.2 MCTS

Store for each edge (s,a):

- N visit count
- W total backed-up value
- Q = W / N
- P prior from network

Per simulation:

1. Selection with PUCT.
2. Expansion at first unseen leaf.
3. Network inference at leaf for priors and value.
4. Backup to root.

## 5.3 Replay Buffer

Store tuples:

- obs
- pi_target (from MCTS root visits)
- z_target (episode return-to-go)

## 6. Minimal File Layout in RL/mcts

- alphazero_agent.py
- mcts.py
- model_adapter.py
- replay_buffer.py
- worker.py
- train.py
- config.py

That is enough for an MVP.

## 7. Compatibility with Existing RL/models

The adapter is where model-specific logic lives.

Required behavior for any adapter implementation:

1. Convert env observation to the model input format.
2. Run model forward pass.
3. Convert model output to:
  - priors over all env actions, shape (A,)
  - scalar value

Example mappings:

- If model returns policy logits: apply softmax to get priors.
- If model returns policy probabilities: use directly as priors.
- If model returns a list of per-component policies: select the current component policy and map to env action index order.
- If model returns value tensor with shape (1,) or (B,): extract scalar for current state.

This keeps the MCTS core unchanged while still being compatible with StatePrep-style model outputs.

## 8. Minimal Training Loop

1. Collect episodes with MCTS policy improvement (parallel CPU workers).
2. Add trajectory samples to replay buffer.
3. Sample minibatches.
4. Optimize on one learner GPU, then refresh inference replicas on other GPUs:
   - policy loss: cross-entropy with `pi_target`
   - value loss: MSE with `z_target`
5. Repeat.

Pseudo-structure:

```text
for iteration in range(num_iterations):
    # 1) Make sure all inference GPUs have the latest learner weights.
    push_weights_to_inference_replicas()

    # 2) Collect trajectories via parallel CPU workers + GPU inference replicas.
    trajectories = collect_parallel(
        num_workers=num_cpu_workers,
        episodes=episodes_per_iter,
        model_adapter=model_adapter,
    )
    buffer.add_many(to_obs_pi_z(trajectories, gamma))

    # 3) Train only on the learner GPU.
    for _ in range(gradient_steps):
        obs, pi, z = buffer.sample(batch_size)
        logits, v = learner_model(obs)  # model on learner GPU only
        loss_policy = cross_entropy_with_soft_targets(logits, pi)
        loss_value = mse(v, z)
        loss = loss_policy + value_coef * loss_value
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    # 4) Push updated weights again before next collection phase.
    push_weights_to_inference_replicas()
```

## 9. Minimal Defaults

Use these starting values:

- `num_simulations = 64`
- `c_puct = 1.5`
- `gamma = 0.99`
- `tau = 1.0` during training, `tau = 0.0` in evaluation
- `learning_rate = 3e-4`
- `batch_size = 64`
- `num_cpu_workers = os.cpu_count()` (or smaller if env is heavy)
- `num_inference_gpus = max(1, torch.cuda.device_count() - 1)`
- `learner_gpu_id = 0`
- `inference_gpu_ids = [1..N-1]` if `N > 1`, else `[0]`
- `weight_sync_every = 1` training iteration

## 10. CUDA (Arbitrary Number of GPUs)

Use one code path with graceful scaling:

1. `num_gpus == 0`: CPU fallback.
2. `num_gpus == 1`: one GPU does both inference and training.
3. `num_gpus >= 2`: one learner GPU + replicated inference GPUs.

Recommended setup (no DDP):

- Keep one authoritative learner model on `learner_gpu_id`.
- Keep read-only inference replicas on `inference_gpu_ids`.
- After each training block, copy learner `state_dict` to all inference replicas.
- Save checkpoints from the learner model only.

Inference for MCTS workers:

- Keep MCTS workers on CPU.
- Send batched leaf observations to an inference service that load-balances across inference GPUs.
- Return `(priors, value)` to workers.

Why this matches your bottleneck:

- Tree search stays CPU-parallel.
- The expensive neural forward pass scales with number of inference GPUs.
- Training remains simple on one GPU (no DDP complexity).

Implementation note for sync:

- Use `with torch.no_grad(): replica.load_state_dict(learner.state_dict(), strict=True)`.
- If replicas are in separate processes, broadcast serialized weights via multiprocessing queues or shared memory.

Versioned barrier protocol (no stale inference):

1. Pause intake of new inference requests for the old model version.
2. Drain all in-flight old-version requests to completion.
3. Verify each inference worker reports zero active old-version requests.
4. Load new learner weights into every inference replica.
5. Resume intake with the new model version only.

Operational rule:

- A training iteration can start rollout collection only after all replicas ACK the same `model_version`.
- Every inference request/response carries `model_version` for auditing and safety checks.

## 11. Parallel Tree Search (Arbitrary Number of CPUs)

Use root-parallel search with independent workers:

1. Spawn `num_cpu_workers` processes.
2. Each worker runs complete MCTS simulations on its own env clone.
3. Merge root visit counts across workers.
4. Build final root policy from merged counts.

Why root-parallel first:

- Simple and stable.
- No shared mutable tree locks.
- Easy to scale from 1 worker to many workers.

Merging rule:

- `N_total(a) = sum_w N_w(a)`
- Optionally merge `W` as sum and recompute `Q = W_total / N_total`.

Set total simulations as:

- `num_simulations_total = sims_per_worker * num_cpu_workers`

## 12. What We Intentionally Exclude

- Dirichlet root noise
- Action masking
- Transposition tables
- Continuous-action support
- MuZero dynamics model

These can be added later, but are unnecessary for a clear first implementation.

## 13. MVP Checklist

- Run on one Discrete Gym environment end-to-end.
- MCTS returns non-uniform policies (not random forever).
- Training loss decreases over time.
- Average episode return improves over baseline random policy.

If these four pass, the minimal AlphaZero pipeline is working.
