# Code-Ready AutoEncoder Implementation Spec

status: DRAFT
updated: 2026-05-04

This document turns the memory-aware AE model descriptions into implementation
contracts. The intent is that an engineer can create `src/models/ae.py` and
`analysis/.../run.py` directly from this spec.

## Scope

This spec covers only the model and scoring interface:

- input tensor contract,
- feature index slices,
- model IDs and configs,
- PyTorch implementation skeletons,
- anomaly score function,
- ONNX/MNN export constraints.

It does not define dataset loading, split policy, training loop, MNN conversion
commands, or memory measurement harness. Those should be implemented as separate
reproducible experiment artifacts.

## Common Tensor Contract

All AE models must implement the same forward contract:

```python
import torch
from torch import Tensor, nn

class AutoEncoder(nn.Module):
    def forward(self, x: Tensor) -> Tensor:
        """Reconstruct x.

        Args:
            x: Float tensor with shape [B, N, D].

        Returns:
            x_hat: Float tensor with shape [B, N, D].
        """
        ...
```

Initial constants:

```python
DEFAULT_N = 12
DEFAULT_D = 40
DEFAULT_BATCH = 1
```

The model must not change the external shape. It receives normalized 10-second
statistics and returns reconstructed normalized 10-second statistics.

## Feature Layout

Freeze this order in the feature extractor before training:

```python
FEATURE_SLICES = {
    "rw_counts_bytes": slice(0, 4),
    "read_lba_hist": slice(4, 12),
    "write_lba_hist": slice(12, 20),
    "read_len_hist": slice(20, 28),
    "write_len_hist": slice(28, 36),
    "sequentiality": slice(36, 38),
    "optional_compression_or_pad": slice(38, 40),
}
```

Expected frame layout:

```text
frame_10s[D=40] =
  rw_counts_bytes[4],
  read_lba_hist[8],
  write_lba_hist[8],
  read_len_hist[8],
  write_len_hist[8],
  sequentiality[2],
  optional_compression_or_pad[2]
```

Metadata-only evaluation should either keep the last two dimensions as zeroed
pad values or train/export a separate `D=38` model. Do not mix `D=38` and
`D=40` tensors in one MNN graph.

## Config Schema

Use an explicit config object rather than hard-coding model choices in scripts.

```python
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class AEConfig:
    model_id: str
    n_frames: int = 12
    d_features: int = 40
    latent_dim: int = 8
    hidden_dim: int = 24
    frame_embed_dim: int = 12
    conv_channels: int = 24
    conv_bottleneck_channels: int = 8
    kernel_size: int = 3
    activation: str = "relu"
    output_activation: Optional[str] = None
```

Recommended initial configs:

```python
AE0 = AEConfig(model_id="ae0_linear_tiny", latent_dim=8, hidden_dim=32)
AE1 = AEConfig(model_id="ae1_flat_mlp", latent_dim=4, hidden_dim=64)
AE2 = AEConfig(model_id="ae2_shared_frame", latent_dim=8, frame_embed_dim=12)
AE3A = AEConfig(model_id="ae3_gru", hidden_dim=24)
AE3B = AEConfig(model_id="ae3_gru", hidden_dim=32)
AE4 = AEConfig(model_id="ae4_tcn", conv_channels=24, conv_bottleneck_channels=8)
AE5 = AEConfig(model_id="ae5_cnn_gru", hidden_dim=24, frame_embed_dim=16)
```

## Shared Helpers

```python
def make_activation(name: str) -> nn.Module:
    if name == "relu":
        return nn.ReLU()
    if name == "clipped_relu":
        return nn.Hardtanh(min_val=0.0, max_val=6.0)
    raise ValueError(f"unsupported activation: {name}")


def assert_3d_input(x: Tensor, n_frames: int, d_features: int) -> None:
    if x.ndim != 3:
        raise ValueError(f"expected [B,N,D], got {tuple(x.shape)}")
    if x.shape[1] != n_frames or x.shape[2] != d_features:
        raise ValueError(
            f"expected [B,{n_frames},{d_features}], got {tuple(x.shape)}"
        )
```

The checks can be disabled in the exported model path if they interfere with
ONNX tracing. Keep them in training/evaluation code.

## AE-0: Linear Tiny AE

Use this as the minimum AE baseline.

Config:

```python
AEConfig(model_id="ae0_linear_tiny", n_frames=12, d_features=40, latent_dim=8)
```

Architecture for `N=12`, `D=40`:

```text
[B,12,40] -> flatten [B,480]
Dense 480 -> 32 -> ReLU
Dense 32 -> 8 -> ReLU
Dense 8 -> 32 -> ReLU
Dense 32 -> 480 -> linear
reshape [B,12,40]
```

PyTorch skeleton:

```python
class AE0LinearTiny(nn.Module):
    def __init__(self, cfg: AEConfig):
        super().__init__()
        self.cfg = cfg
        l_in = cfg.n_frames * cfg.d_features
        self.net = nn.Sequential(
            nn.Flatten(start_dim=1),
            nn.Linear(l_in, 32),
            make_activation(cfg.activation),
            nn.Linear(32, cfg.latent_dim),
            make_activation(cfg.activation),
            nn.Linear(cfg.latent_dim, 32),
            make_activation(cfg.activation),
            nn.Linear(32, l_in),
        )

    def forward(self, x: Tensor) -> Tensor:
        assert_3d_input(x, self.cfg.n_frames, self.cfg.d_features)
        y = self.net(x)
        return y.reshape(x.shape[0], self.cfg.n_frames, self.cfg.d_features)
```

Implementation notes:

- Set `latent_dim=8`.
- Use this to verify feature normalization and training plumbing.
- If AE-0 is already strong, inspect whether intensity features dominate.

## AE-1: Flat MLP AE

Use this as the stronger flattened baseline.

Config:

```python
AEConfig(model_id="ae1_flat_mlp", n_frames=12, d_features=40, latent_dim=4)
```

Architecture:

```text
[B,12,40] -> flatten [B,480]
Dense 480 -> 64 -> ReLU
Dense 64 -> 16 -> ReLU
Dense 16 -> 4 -> ReLU
Dense 4 -> 16 -> ReLU
Dense 16 -> 64 -> ReLU
Dense 64 -> 480 -> linear
reshape [B,12,40]
```

PyTorch skeleton:

```python
class AE1FlatMLP(nn.Module):
    def __init__(self, cfg: AEConfig):
        super().__init__()
        self.cfg = cfg
        l_in = cfg.n_frames * cfg.d_features
        self.net = nn.Sequential(
            nn.Flatten(start_dim=1),
            nn.Linear(l_in, 64),
            make_activation(cfg.activation),
            nn.Linear(64, 16),
            make_activation(cfg.activation),
            nn.Linear(16, cfg.latent_dim),
            make_activation(cfg.activation),
            nn.Linear(cfg.latent_dim, 16),
            make_activation(cfg.activation),
            nn.Linear(16, 64),
            make_activation(cfg.activation),
            nn.Linear(64, l_in),
        )

    def forward(self, x: Tensor) -> Tensor:
        assert_3d_input(x, self.cfg.n_frames, self.cfg.d_features)
        y = self.net(x)
        return y.reshape(x.shape[0], self.cfg.n_frames, self.cfg.d_features)
```

Implementation notes:

- Set `latent_dim=4`.
- FP32 weights are near the initial weight budget at `N=12`; prefer FP16/Int8
  checks before treating it as deployable.

## AE-2: Shared-Frame Bottleneck AE

Use this as the first serious deployable candidate.

Config:

```python
AEConfig(
    model_id="ae2_shared_frame",
    n_frames=12,
    d_features=40,
    frame_embed_dim=12,
    latent_dim=8,
)
```

Architecture:

```text
[B,12,40]
TimeDistributed Dense 40 -> 24 -> ReLU      [B,12,24]
TimeDistributed Dense 24 -> 12 -> ReLU      [B,12,12]
flatten sequence                            [B,144]
Dense 144 -> 32 -> ReLU                     [B,32]
Dense 32 -> 8 -> ReLU                       [B,8]
Dense 8 -> 32 -> ReLU                       [B,32]
Dense 32 -> 144 -> ReLU                     [B,144]
reshape                                     [B,12,12]
TimeDistributed Dense 12 -> 24 -> ReLU      [B,12,24]
TimeDistributed Dense 24 -> 40 -> linear    [B,12,40]
```

PyTorch skeleton:

```python
class AE2SharedFrame(nn.Module):
    def __init__(self, cfg: AEConfig):
        super().__init__()
        self.cfg = cfg
        n = cfg.n_frames
        d = cfg.d_features
        e = cfg.frame_embed_dim
        self.frame_encoder = nn.Sequential(
            nn.Linear(d, 24),
            make_activation(cfg.activation),
            nn.Linear(24, e),
            make_activation(cfg.activation),
        )
        self.seq_encoder = nn.Sequential(
            nn.Linear(n * e, 32),
            make_activation(cfg.activation),
            nn.Linear(32, cfg.latent_dim),
            make_activation(cfg.activation),
        )
        self.seq_decoder = nn.Sequential(
            nn.Linear(cfg.latent_dim, 32),
            make_activation(cfg.activation),
            nn.Linear(32, n * e),
            make_activation(cfg.activation),
        )
        self.frame_decoder = nn.Sequential(
            nn.Linear(e, 24),
            make_activation(cfg.activation),
            nn.Linear(24, d),
        )

    def forward(self, x: Tensor) -> Tensor:
        assert_3d_input(x, self.cfg.n_frames, self.cfg.d_features)
        b = x.shape[0]
        z_frame = self.frame_encoder(x)
        z = self.seq_encoder(z_frame.reshape(b, -1))
        y_frame = self.seq_decoder(z).reshape(b, self.cfg.n_frames, self.cfg.frame_embed_dim)
        return self.frame_decoder(y_frame)
```

Implementation notes:

- This model uses only Dense/ReLU/Reshape, which is friendly for ONNX and MNN.
- The frame encoder/decoder weights are shared across all `N` frames.
- If `N` changes, only the two sequence dense layers change.

## AE-3: GRU Seq2Seq AE

Use this when explicit temporal order matters.

Config:

```python
AEConfig(model_id="ae3_gru", n_frames=12, d_features=40, hidden_dim=24)
```

Architecture:

```text
[B,12,40]
GRU encoder input_size=40 hidden_size=H      final h [1,B,H]
repeat h over N frames                       [B,12,H]
GRU decoder input_size=H hidden_size=H        [B,12,H]
TimeDistributed Dense H -> 40 -> linear      [B,12,40]
```

PyTorch skeleton:

```python
class AE3GRUSeq2Seq(nn.Module):
    def __init__(self, cfg: AEConfig):
        super().__init__()
        self.cfg = cfg
        h = cfg.hidden_dim
        self.encoder = nn.GRU(
            input_size=cfg.d_features,
            hidden_size=h,
            num_layers=1,
            batch_first=True,
        )
        self.decoder = nn.GRU(
            input_size=h,
            hidden_size=h,
            num_layers=1,
            batch_first=True,
        )
        self.output = nn.Linear(h, cfg.d_features)

    def forward(self, x: Tensor) -> Tensor:
        assert_3d_input(x, self.cfg.n_frames, self.cfg.d_features)
        _, h_last = self.encoder(x)
        context = h_last[-1].unsqueeze(1).repeat(1, self.cfg.n_frames, 1)
        dec, _ = self.decoder(context)
        return self.output(dec)
```

Implementation notes:

- Start with `hidden_dim=24`; test `hidden_dim=32` only if underfitting is clear.
- Verify GRU export and MNN runtime memory early.
- If ONNX export of GRU creates problematic operators, prefer AE-4.

## AE-4: Temporal Conv1D AE

Use this as the most MNN-friendly temporal candidate.

Config:

```python
AEConfig(
    model_id="ae4_tcn",
    n_frames=12,
    d_features=40,
    conv_channels=24,
    conv_bottleneck_channels=8,
    kernel_size=3,
)
```

Architecture:

```text
[B,12,40]
transpose to channels-first                  [B,40,12]
Conv1d 40 -> 24, K=3, pad=1 -> ReLU          [B,24,12]
Conv1d 24 -> 24, K=3, pad=1 -> ReLU          [B,24,12]
Conv1d 24 -> 8, K=1 -> ReLU                  [B,8,12]
Conv1d 8 -> 24, K=1 -> ReLU                  [B,24,12]
Conv1d 24 -> 24, K=3, pad=1 -> ReLU          [B,24,12]
Conv1d 24 -> 40, K=3, pad=1 -> linear        [B,40,12]
transpose back                               [B,12,40]
```

PyTorch skeleton:

```python
class AE4TemporalConv(nn.Module):
    def __init__(self, cfg: AEConfig):
        super().__init__()
        self.cfg = cfg
        c = cfg.conv_channels
        z = cfg.conv_bottleneck_channels
        k = cfg.kernel_size
        p = k // 2
        self.net = nn.Sequential(
            nn.Conv1d(cfg.d_features, c, kernel_size=k, padding=p),
            make_activation(cfg.activation),
            nn.Conv1d(c, c, kernel_size=k, padding=p),
            make_activation(cfg.activation),
            nn.Conv1d(c, z, kernel_size=1),
            make_activation(cfg.activation),
            nn.Conv1d(z, c, kernel_size=1),
            make_activation(cfg.activation),
            nn.Conv1d(c, c, kernel_size=k, padding=p),
            make_activation(cfg.activation),
            nn.Conv1d(c, cfg.d_features, kernel_size=k, padding=p),
        )

    def forward(self, x: Tensor) -> Tensor:
        assert_3d_input(x, self.cfg.n_frames, self.cfg.d_features)
        y = x.transpose(1, 2)
        y = self.net(y)
        return y.transpose(1, 2)
```

Implementation notes:

- Keep `kernel_size=3` and static padding for the first export.
- In MNN, this may appear as Conv1D or Conv2D depending on export path.
- Weight count is almost independent of `N`, but activation memory grows with
  `N * conv_channels`.

## AE-5: Tiny CNN-GRU AE

Use this to test the original CNN-GRU hypothesis after simpler candidates.

Config:

```python
AEConfig(model_id="ae5_cnn_gru", n_frames=12, d_features=40, hidden_dim=24)
```

Architecture:

```text
[B,12,40]
reshape per frame to 5 groups x 8 bins       [B,12,5,8]
merge B,N,groups for bucket CNN              [B*12*5,1,8]
Conv1d 1 -> 8, K=3, pad=1 -> ReLU            [B*12*5,8,8]
Conv1d 8 -> 8, K=3, pad=1 -> ReLU            [B*12*5,8,8]
flatten per frame                            [B,12,320]
Dense 320 -> 16 -> ReLU                      [B,12,16]
GRU encoder hidden H                         [1,B,H]
repeat context                               [B,12,H]
GRU decoder                                  [B,12,H]
Dense H -> 40 -> linear                      [B,12,40]
```

PyTorch skeleton:

```python
class AE5TinyCNNGRU(nn.Module):
    def __init__(self, cfg: AEConfig):
        super().__init__()
        self.cfg = cfg
        self.groups = 5
        self.bucket_width = 8
        if cfg.d_features != self.groups * self.bucket_width:
            raise ValueError("AE5 expects D=40 as 5 groups x 8 buckets")
        self.bucket_cnn = nn.Sequential(
            nn.Conv1d(1, 8, kernel_size=3, padding=1),
            make_activation(cfg.activation),
            nn.Conv1d(8, 8, kernel_size=3, padding=1),
            make_activation(cfg.activation),
        )
        self.frame_proj = nn.Sequential(
            nn.Linear(self.groups * 8 * self.bucket_width, cfg.frame_embed_dim),
            make_activation(cfg.activation),
        )
        self.encoder = nn.GRU(
            input_size=cfg.frame_embed_dim,
            hidden_size=cfg.hidden_dim,
            num_layers=1,
            batch_first=True,
        )
        self.decoder = nn.GRU(
            input_size=cfg.hidden_dim,
            hidden_size=cfg.hidden_dim,
            num_layers=1,
            batch_first=True,
        )
        self.output = nn.Linear(cfg.hidden_dim, cfg.d_features)

    def forward(self, x: Tensor) -> Tensor:
        assert_3d_input(x, self.cfg.n_frames, self.cfg.d_features)
        b, n, _ = x.shape
        y = x.reshape(b, n, self.groups, self.bucket_width)
        y = y.reshape(b * n * self.groups, 1, self.bucket_width)
        y = self.bucket_cnn(y)
        y = y.reshape(b, n, self.groups * 8 * self.bucket_width)
        y = self.frame_proj(y)
        _, h_last = self.encoder(y)
        context = h_last[-1].unsqueeze(1).repeat(1, self.cfg.n_frames, 1)
        dec, _ = self.decoder(context)
        return self.output(dec)
```

Implementation notes:

- This model assumes `D=40` and the 5-by-8 feature layout.
- The fifth group contains scalar features and padding, so the CNN locality is
  less natural there.
- Use only after AE-2, AE-3, and AE-4 establish the quality/memory curve.

## Builder Function

Use one builder entry point so experiment configs can select models by ID:

```python
def build_autoencoder(cfg: AEConfig) -> nn.Module:
    if cfg.model_id == "ae0_linear_tiny":
        return AE0LinearTiny(cfg)
    if cfg.model_id == "ae1_flat_mlp":
        return AE1FlatMLP(cfg)
    if cfg.model_id == "ae2_shared_frame":
        return AE2SharedFrame(cfg)
    if cfg.model_id == "ae3_gru":
        return AE3GRUSeq2Seq(cfg)
    if cfg.model_id == "ae4_tcn":
        return AE4TemporalConv(cfg)
    if cfg.model_id == "ae5_cnn_gru":
        return AE5TinyCNNGRU(cfg)
    raise ValueError(f"unknown model_id: {cfg.model_id}")
```

## Reconstruction Loss

Training should start with weighted MSE by feature family.

```python
FEATURE_WEIGHTS = {
    "rw_counts_bytes": 1.0,
    "read_lba_hist": 1.0,
    "write_lba_hist": 1.0,
    "read_len_hist": 1.0,
    "write_len_hist": 1.0,
    "sequentiality": 0.5,
    "optional_compression_or_pad": 0.5,
}


def reconstruction_error_by_family(x: Tensor, x_hat: Tensor) -> dict[str, Tensor]:
    err = (x_hat - x).pow(2)
    return {
        name: err[:, :, sl].mean(dim=(1, 2))
        for name, sl in FEATURE_SLICES.items()
    }


def anomaly_score(x: Tensor, x_hat: Tensor) -> Tensor:
    by_family = reconstruction_error_by_family(x, x_hat)
    score = None
    weight_sum = 0.0
    for name, value in by_family.items():
        w = FEATURE_WEIGHTS[name]
        score = value * w if score is None else score + value * w
        weight_sum += w
    return score / weight_sum


def training_loss(x: Tensor, x_hat: Tensor) -> Tensor:
    return anomaly_score(x, x_hat).mean()
```

For the first implementation, keep the same function for training loss and
offline anomaly score. Later experiments may switch histogram groups to Huber or
Jensen-Shannon loss, but that should be an explicit ablation.

## ONNX Export Contract

Export one fixed-shape graph per selected `N` and `D`.

```python
def export_onnx(model: nn.Module, cfg: AEConfig, path: str) -> None:
    model.eval()
    dummy = torch.zeros(1, cfg.n_frames, cfg.d_features, dtype=torch.float32)
    torch.onnx.export(
        model,
        dummy,
        path,
        input_names=["x"],
        output_names=["x_hat"],
        dynamic_axes=None,
        opset_version=17,
    )
```

Export rules:

- Use batch size 1 for MNN deployment tests.
- Do not export thresholding or anomaly-score calculation in the first graph.
- Avoid dynamic axes; MNN memory measurement should use fixed shapes.
- Store `cfg`, feature slice order, and normalization constants next to the
  exported model.

## Minimal Smoke Test

Every model implementation should pass this before training:

```python
def smoke_test_model(cfg: AEConfig) -> None:
    model = build_autoencoder(cfg)
    x = torch.randn(1, cfg.n_frames, cfg.d_features)
    x_hat = model(x)
    assert x_hat.shape == x.shape
    loss = training_loss(x, x_hat)
    assert loss.ndim == 0
    loss.backward()
```

Run this for:

```python
for cfg in [AE0, AE1, AE2, AE3A, AE3B, AE4, AE5]:
    smoke_test_model(cfg)
```

## Initial Implementation Order

Implement in this order:

1. `AE0LinearTiny`: validates tensors, loss, training loop, and metrics.
2. `AE2SharedFrame`: first serious dense-only deployment candidate.
3. `AE4TemporalConv`: first serious temporal model with MNN-friendly operators.
4. `AE3GRUSeq2Seq`: temporal model if GRU export and memory are acceptable.
5. `AE5TinyCNNGRU`: original-hypothesis model after simpler candidates are
   measured.

The first experiment should compare AE-0, AE-2, and AE-4 before spending time on
CNN-GRU. That comparison tells whether temporal structure and per-frame
structure matter under the 500 KB model-memory budget.
