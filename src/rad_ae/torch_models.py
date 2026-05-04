"""Optional PyTorch AE candidates for full offline experiments.

The repository's smoke path does not require PyTorch. When a research machine
has PyTorch installed, these modules provide the AE-2 through AE-5 candidates
from the feature/model plan.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TorchAEConfig:
    model_type: str = "cnn_gru"
    sequence_length: int = 12
    d_features: int = 12
    latent_dim: int = 8
    frame_embed_dim: int = 16
    frame_latent_dim: int = 8
    conv_channels: int = 24
    hidden_dim: int = 24


def require_torch():
    try:
        import torch
        import torch.nn as nn
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "PyTorch is required for temporal AE candidates. "
            "Use model.type=numpy_mlp for the dependency-light baseline."
        ) from exc
    return torch, nn


def build_torch_autoencoder(config: TorchAEConfig):
    torch, nn = require_torch()

    if config.model_type == "two_level_dense":
        return _TwoLevelDenseAutoEncoder(nn, config)
    if config.model_type == "gru":
        return _GruAutoEncoder(nn, config)
    if config.model_type == "tcn":
        return _TemporalConvAutoEncoder(nn, config)
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
                self.bottleneck = nn.Sequential(
                    nn.Linear(config.hidden_dim, config.latent_dim),
                    nn.ReLU(),
                    nn.Linear(config.latent_dim, config.hidden_dim),
                    nn.ReLU(),
                )
                self.decoder = nn.GRU(config.hidden_dim, config.hidden_dim, batch_first=True)
                self.head = nn.Linear(config.hidden_dim, frame_dim)

            def forward(self, x):
                batch = x.shape[0]
                flat = x.reshape(batch, config.sequence_length, frame_dim)
                context, _ = self.encoder(flat)
                seed = self.bottleneck(context)
                decoded, _ = self.decoder(seed)
                out = self.head(decoded)
                return out.reshape(batch, config.sequence_length, config.d_features)

        return GruAutoEncoder()


class _TwoLevelDenseAutoEncoder:
    def __new__(cls, nn, config: TorchAEConfig):
        frame_dim = config.d_features
        frame_embed = config.frame_embed_dim
        frame_latent = config.frame_latent_dim
        sequence_latent_dim = config.sequence_length * frame_latent

        class TwoLevelDenseAutoEncoder(nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.frame_encoder = nn.Sequential(
                    nn.Linear(frame_dim, frame_embed),
                    nn.ReLU(),
                    nn.Linear(frame_embed, frame_latent),
                    nn.ReLU(),
                )
                self.sequence_bottleneck = nn.Sequential(
                    nn.Linear(sequence_latent_dim, config.hidden_dim),
                    nn.ReLU(),
                    nn.Linear(config.hidden_dim, config.latent_dim),
                    nn.ReLU(),
                    nn.Linear(config.latent_dim, config.hidden_dim),
                    nn.ReLU(),
                    nn.Linear(config.hidden_dim, sequence_latent_dim),
                    nn.ReLU(),
                )
                self.frame_decoder = nn.Sequential(
                    nn.Linear(frame_latent, frame_embed),
                    nn.ReLU(),
                    nn.Linear(frame_embed, frame_dim),
                )

            def forward(self, x):
                batch = x.shape[0]
                frame_code = self.frame_encoder(x)
                seq_code = frame_code.reshape(batch, sequence_latent_dim)
                seq_recon = self.sequence_bottleneck(seq_code)
                frame_recon = seq_recon.reshape(batch, config.sequence_length, frame_latent)
                return self.frame_decoder(frame_recon)

        return TwoLevelDenseAutoEncoder()


class _TemporalConvAutoEncoder:
    def __new__(cls, nn, config: TorchAEConfig):
        class TemporalConvAutoEncoder(nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.encoder = nn.Sequential(
                    nn.Conv1d(config.d_features, config.conv_channels, kernel_size=3, padding=1),
                    nn.ReLU(),
                    nn.Conv1d(config.conv_channels, config.conv_channels, kernel_size=3, padding=1),
                    nn.ReLU(),
                )
                self.bottleneck = nn.Sequential(
                    nn.Linear(config.conv_channels, config.frame_latent_dim),
                    nn.ReLU(),
                    nn.Linear(config.frame_latent_dim, config.conv_channels),
                    nn.ReLU(),
                )
                self.decoder = nn.Sequential(
                    nn.Conv1d(config.conv_channels, config.conv_channels, kernel_size=3, padding=1),
                    nn.ReLU(),
                    nn.Conv1d(config.conv_channels, config.d_features, kernel_size=3, padding=1),
                )

            def forward(self, x):
                encoded = self.encoder(x.transpose(1, 2)).transpose(1, 2)
                restored = self.bottleneck(encoded)
                return self.decoder(restored.transpose(1, 2)).transpose(1, 2)

        return TemporalConvAutoEncoder()


class _TinyCnnGruAutoEncoder:
    def __new__(cls, nn, config: TorchAEConfig):
        class TinyCnnGruAutoEncoder(nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.temporal_cnn = nn.Sequential(
                    nn.Conv1d(config.d_features, config.conv_channels, kernel_size=1),
                    nn.ReLU(),
                )
                self.frame_code = nn.Sequential(
                    nn.Linear(config.conv_channels, config.frame_embed_dim),
                    nn.ReLU(),
                )
                self.encoder = nn.GRU(config.frame_embed_dim, config.hidden_dim, batch_first=True)
                self.bottleneck = nn.Sequential(
                    nn.Linear(config.hidden_dim, config.latent_dim),
                    nn.ReLU(),
                )
                self.expansion = nn.Sequential(
                    nn.Linear(config.latent_dim, config.hidden_dim),
                    nn.ReLU(),
                )
                self.decoder = nn.GRU(config.hidden_dim, config.hidden_dim, batch_first=True)
                self.head = nn.Linear(config.hidden_dim, config.d_features)

            def forward(self, x):
                batch = x.shape[0]
                embedded = self.temporal_cnn(x.transpose(1, 2)).transpose(1, 2)
                frame_code = self.frame_code(embedded)
                context, _ = self.encoder(frame_code)
                z = self.bottleneck(context)
                seed = self.expansion(z)
                decoded, _ = self.decoder(seed)
                out = self.head(decoded)
                return out.reshape(batch, config.sequence_length, config.d_features)

        return TinyCnnGruAutoEncoder()
