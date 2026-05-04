"""Small AutoEncoder candidates that can be trained in offline studies."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class NumpyMLPAEConfig:
    input_dim: int
    latent_dim: int = 16
    learning_rate: float = 0.001
    epochs: int = 50
    batch_size: int = 64
    seed: int = 0

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class NumpyMLPAutoEncoder:
    """One-hidden-layer bottleneck AE with Adam updates.

    This is the memory-first baseline from the research plan. The CNN-GRU
    architecture is implemented separately as an optional PyTorch model; this
    NumPy model gives the repository a dependency-light path for reproducible
    smoke checks and baseline public-data runs.
    """

    def __init__(self, config: NumpyMLPAEConfig) -> None:
        self.config = config
        rng = np.random.default_rng(config.seed)
        limit1 = np.sqrt(6.0 / (config.input_dim + config.latent_dim))
        limit2 = np.sqrt(6.0 / (config.latent_dim + config.input_dim))
        self.w1 = rng.uniform(-limit1, limit1, size=(config.input_dim, config.latent_dim)).astype(np.float32)
        self.b1 = np.zeros((config.latent_dim,), dtype=np.float32)
        self.w2 = rng.uniform(-limit2, limit2, size=(config.latent_dim, config.input_dim)).astype(np.float32)
        self.b2 = np.zeros((config.input_dim,), dtype=np.float32)
        self.loss_history: list[float] = []

    def fit(self, x: np.ndarray, loss_weights: np.ndarray | None = None) -> "NumpyMLPAutoEncoder":
        if x.ndim != 2:
            raise ValueError("NumpyMLPAutoEncoder.fit expects a 2-D flattened array")
        if x.shape[0] == 0:
            raise ValueError("cannot train AutoEncoder on an empty array")
        if loss_weights is not None and loss_weights.shape != x.shape:
            raise ValueError("loss_weights must have the same shape as x")

        rng = np.random.default_rng(self.config.seed)
        state = _AdamState.for_parameters((self.w1, self.b1, self.w2, self.b2))
        for _epoch in range(self.config.epochs):
            order = rng.permutation(x.shape[0])
            epoch_losses: list[float] = []
            for start in range(0, x.shape[0], self.config.batch_size):
                batch_indices = order[start : start + self.config.batch_size]
                batch = x[batch_indices]
                batch_weights = loss_weights[batch_indices] if loss_weights is not None else None
                recon, latent = self._forward(batch)
                diff = recon - batch
                denominator = _loss_denominator(diff, batch_weights)
                weighted_diff = diff if batch_weights is None else diff * batch_weights
                loss = float(np.sum(diff * weighted_diff) / denominator)
                epoch_losses.append(loss)
                grads = self._backward(batch, recon, latent, batch_weights)
                state.update(
                    (self.w1, self.b1, self.w2, self.b2),
                    grads,
                    learning_rate=self.config.learning_rate,
                )
            self.loss_history.append(float(np.mean(epoch_losses)))
        return self

    def reconstruct(self, x: np.ndarray) -> np.ndarray:
        return self._forward(x)[0]

    def score(self, x: np.ndarray, loss_weights: np.ndarray | None = None) -> np.ndarray:
        recon = self.reconstruct(x)
        err = (recon - x) ** 2
        if loss_weights is None:
            return np.mean(err, axis=1)
        if loss_weights.shape != x.shape:
            raise ValueError("loss_weights must have the same shape as x")
        denominator = np.maximum(np.sum(loss_weights, axis=1), 1.0)
        return np.sum(err * loss_weights, axis=1) / denominator

    def save(self, path: Path | str) -> None:
        np.savez_compressed(
            path,
            w1=self.w1,
            b1=self.b1,
            w2=self.w2,
            b2=self.b2,
            config=np.array([self.config.to_dict()], dtype=object),
            loss_history=np.asarray(self.loss_history, dtype=np.float32),
        )

    @property
    def parameter_count(self) -> int:
        return int(self.w1.size + self.b1.size + self.w2.size + self.b2.size)

    def memory_estimate(self, dtype_bytes: int = 4) -> dict[str, int]:
        weight_bytes = self.parameter_count * dtype_bytes
        input_bytes = self.config.input_dim * dtype_bytes
        latent_bytes = self.config.latent_dim * dtype_bytes
        return {
            "parameter_count": self.parameter_count,
            "weight_bytes_fp32": weight_bytes,
            "weight_bytes_int8": self.parameter_count,
            "single_input_bytes_fp32": input_bytes,
            "single_latent_bytes_fp32": latent_bytes,
            "rough_model_path_bytes_fp32": weight_bytes + (2 * input_bytes) + latent_bytes,
        }

    def _forward(self, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        latent = np.tanh(x @ self.w1 + self.b1)
        recon = latent @ self.w2 + self.b2
        return recon.astype(np.float32), latent.astype(np.float32)

    def _backward(
        self,
        x: np.ndarray,
        recon: np.ndarray,
        latent: np.ndarray,
        loss_weights: np.ndarray | None,
    ) -> tuple[np.ndarray, ...]:
        denominator = _loss_denominator(recon - x, loss_weights)
        d_recon = 2.0 * (recon - x) / denominator
        if loss_weights is not None:
            d_recon *= loss_weights
        grad_w2 = latent.T @ d_recon
        grad_b2 = d_recon.sum(axis=0)
        d_latent = (d_recon @ self.w2.T) * (1.0 - latent * latent)
        grad_w1 = x.T @ d_latent
        grad_b1 = d_latent.sum(axis=0)
        return (
            grad_w1.astype(np.float32),
            grad_b1.astype(np.float32),
            grad_w2.astype(np.float32),
            grad_b2.astype(np.float32),
        )


def _loss_denominator(diff: np.ndarray, loss_weights: np.ndarray | None) -> float:
    if loss_weights is None:
        return float(max(1, diff.size))
    return max(float(np.sum(loss_weights)), 1.0)


class _AdamState:
    def __init__(self, moments: tuple[np.ndarray, ...], velocities: tuple[np.ndarray, ...]) -> None:
        self.moments = list(moments)
        self.velocities = list(velocities)
        self.step = 0

    @classmethod
    def for_parameters(cls, params: tuple[np.ndarray, ...]) -> "_AdamState":
        return cls(
            tuple(np.zeros_like(param) for param in params),
            tuple(np.zeros_like(param) for param in params),
        )

    def update(
        self,
        params: tuple[np.ndarray, ...],
        grads: tuple[np.ndarray, ...],
        learning_rate: float,
        beta1: float = 0.9,
        beta2: float = 0.999,
        epsilon: float = 1e-8,
    ) -> None:
        self.step += 1
        for idx, (param, grad) in enumerate(zip(params, grads)):
            self.moments[idx] = beta1 * self.moments[idx] + (1.0 - beta1) * grad
            self.velocities[idx] = beta2 * self.velocities[idx] + (1.0 - beta2) * (grad * grad)
            m_hat = self.moments[idx] / (1.0 - beta1**self.step)
            v_hat = self.velocities[idx] / (1.0 - beta2**self.step)
            param -= learning_rate * m_hat / (np.sqrt(v_hat) + epsilon)
