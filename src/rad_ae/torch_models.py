"""Optional PyTorch AE candidates for full offline experiments.

The repository's smoke path does not require PyTorch. When a research machine
has PyTorch installed, these modules provide the GRU and tiny CNN-GRU candidates
from the feature/model plan.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TorchAEConfig:
    model_type: str = "cnn_gru"
    sequence_length: int = 12
    d_features: int = 12
    latent_dim: int = 16
    conv_channels: int = 16
    hidden_dim: int = 24


def require_torch():
    try:
        import torch
        import torch.nn as nn
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "PyTorch is required for GRU/CNN-GRU AE candidates. "
            "Use model.type=numpy_mlp for the dependency-light baseline."
        ) from exc
    return torch, nn


def build_torch_autoencoder(config: TorchAEConfig):
    torch, nn = require_torch()

    if config.model_type == "gru":
        return _GruAutoEncoder(nn, config)
    if config.model_type == "cnn_gru":
        return _TinyCnnGruAutoEncoder(nn, config)
    raise ValueError(f"unknown torch model_type: {config.model_type}")


def count_torch_parameters(model) -> int:
    return int(sum(parameter.numel() for parameter in model.parameters()))


class _GruAutoEncoder:
    def __new__(cls, nn, config: TorchAEConfig):
        frame_dim = config.d_features

        class GruAutoEncoder(nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.encoder = nn.GRU(frame_dim, config.hidden_dim, batch_first=True)
                self.decoder = nn.GRU(config.hidden_dim, config.hidden_dim, batch_first=True)
                self.head = nn.Linear(config.hidden_dim, frame_dim)

            def forward(self, x):
                batch = x.shape[0]
                flat = x.reshape(batch, config.sequence_length, frame_dim)
                _, hidden = self.encoder(flat)
                seed = hidden[-1].unsqueeze(1).repeat(1, config.sequence_length, 1)
                decoded, _ = self.decoder(seed)
                out = self.head(decoded)
                return out.reshape(batch, config.sequence_length, config.d_features)

        return GruAutoEncoder()


class _TinyCnnGruAutoEncoder:
    def __new__(cls, nn, config: TorchAEConfig):
        class TinyCnnGruAutoEncoder(nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.temporal_cnn = nn.Sequential(
                    nn.Conv1d(config.d_features, config.conv_channels, kernel_size=3, padding=1),
                    nn.ReLU(),
                )
                self.encoder = nn.GRU(config.conv_channels, config.hidden_dim, batch_first=True)
                self.decoder = nn.GRU(config.hidden_dim, config.hidden_dim, batch_first=True)
                self.head = nn.Linear(config.hidden_dim, config.d_features)

            def forward(self, x):
                batch = x.shape[0]
                embedded = self.temporal_cnn(x.transpose(1, 2)).transpose(1, 2)
                _, hidden = self.encoder(embedded)
                seed = hidden[-1].unsqueeze(1).repeat(1, config.sequence_length, 1)
                decoded, _ = self.decoder(seed)
                out = self.head(decoded)
                return out.reshape(batch, config.sequence_length, config.d_features)

        return TinyCnnGruAutoEncoder()
