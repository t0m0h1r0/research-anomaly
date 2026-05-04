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
    channels: int = 5
    buckets: int = 8
    sequence_length: int = 12
    latent_dim: int = 16
    conv_channels: int = 8
    gru_hidden_dim: int = 16


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
        frame_dim = config.channels * config.buckets

        class GruAutoEncoder(nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.encoder = nn.GRU(frame_dim, config.gru_hidden_dim, batch_first=True)
                self.to_latent = nn.Linear(config.gru_hidden_dim, config.latent_dim)
                self.from_latent = nn.Linear(config.latent_dim, config.gru_hidden_dim)
                self.decoder = nn.GRU(config.gru_hidden_dim, config.gru_hidden_dim, batch_first=True)
                self.head = nn.Linear(config.gru_hidden_dim, frame_dim)

            def forward(self, x):
                batch = x.shape[0]
                flat = x.reshape(batch, config.sequence_length, frame_dim)
                _, hidden = self.encoder(flat)
                latent = self.to_latent(hidden[-1])
                seed = self.from_latent(latent).unsqueeze(1).repeat(1, config.sequence_length, 1)
                decoded, _ = self.decoder(seed)
                out = self.head(decoded)
                return out.reshape(batch, config.sequence_length, config.channels, config.buckets)

        return GruAutoEncoder()


class _TinyCnnGruAutoEncoder:
    def __new__(cls, nn, config: TorchAEConfig):
        conv_embed_dim = config.conv_channels * config.buckets

        class TinyCnnGruAutoEncoder(nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.window_conv = nn.Sequential(
                    nn.Conv1d(config.channels, config.conv_channels, kernel_size=3, padding=1),
                    nn.ReLU(),
                    nn.Conv1d(config.conv_channels, config.conv_channels, kernel_size=3, padding=1),
                    nn.ReLU(),
                )
                self.window_embed = nn.Linear(conv_embed_dim, config.gru_hidden_dim)
                self.encoder = nn.GRU(config.gru_hidden_dim, config.gru_hidden_dim, batch_first=True)
                self.to_latent = nn.Linear(config.gru_hidden_dim, config.latent_dim)
                self.from_latent = nn.Linear(config.latent_dim, config.gru_hidden_dim)
                self.decoder = nn.GRU(config.gru_hidden_dim, config.gru_hidden_dim, batch_first=True)
                self.head = nn.Linear(config.gru_hidden_dim, config.channels * config.buckets)

            def forward(self, x):
                batch = x.shape[0]
                windows = x.reshape(batch * config.sequence_length, config.channels, config.buckets)
                embedded = self.window_conv(windows).reshape(batch, config.sequence_length, conv_embed_dim)
                embedded = self.window_embed(embedded)
                _, hidden = self.encoder(embedded)
                latent = self.to_latent(hidden[-1])
                seed = self.from_latent(latent).unsqueeze(1).repeat(1, config.sequence_length, 1)
                decoded, _ = self.decoder(seed)
                out = self.head(decoded)
                return out.reshape(batch, config.sequence_length, config.channels, config.buckets)

        return TinyCnnGruAutoEncoder()
