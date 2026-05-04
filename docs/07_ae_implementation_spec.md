# Code-Ready AutoEncoder Implementation Spec

status: DRAFT
updated: 2026-05-04

This document turns the scalar-only memory-aware AE descriptions into
implementation contracts. It intentionally does not assume LBA or transfer-size
histograms. If a target device later exposes cheap bucket counters, that should
be a separate profile and a separate fixed-shape export.

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
DEFAULT_D = 12
DEFAULT_BATCH = 1
```

The model must not change the external shape. It receives normalized 10-second
statistics and returns reconstructed normalized 10-second statistics.

## Feature Layout

Freeze this order in the feature extractor before training:

```python
FEATURE_SLICES = {
    "intensity": slice(0, 2),              # total_count, total_bytes
    "write_ratio": slice(2, 3),            # writes / total_count
    "mean_lba": slice(3, 4),               # total-count-weighted mean LBA
    "mean_length": slice(4, 5),            # total-count-weighted mean length
    "frame_deltas": slice(5, 7),           # delta_mean_lba, delta_mean_len
    "optional_telemetry": slice(7, 8),     # compression/entropy-like if cheap
    "padding": slice(8, 12),               # excluded from loss and score
}
```

Expected frame layout:

```text
frame_10s[D=12] =
  intensity[2],
  write_ratio[1],
  mean_lba[1],
  mean_length[1],
  frame_deltas[2],
  optional_telemetry[1],
  padding[4]
```

Metadata-only evaluation should keep unavailable optional telemetry and padding
as zeroed slots with zero loss/score weights. Empty frames should zero-fill
write ratio, mean LBA, mean length, and dependent deltas, with a separate
loss/score mask. Do not mix narrower tensors and `D=12` tensors in one MNN
graph.

## Config Schema

Use an explicit config object rather than hard-coding model choices in scripts.

```python
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class AEConfig:
    model_id: str
    n_frames: int = 12
    d_features: int = 12
    latent_dim: int = 8
    hidden_dim: int = 24
    frame_embed_dim: int = 12
    frame_latent_dim: int = 8
    conv_channels: int = 24
    kernel_size: int = 3
    activation: str = "relu"
    output_activation: Optional[str] = None
```

Recommended initial configs:

```python
AE0 = AEConfig(model_id="ae0_linear_tiny", latent_dim=8, hidden_dim=32)
AE1 = AEConfig(model_id="ae1_flat_mlp", latent_dim=16, hidden_dim=64)
AE2 = AEConfig(model_id="ae2_two_level_dense", latent_dim=8, hidden_dim=24, frame_embed_dim=16, frame_latent_dim=8)
AE3A = AEConfig(model_id="ae3_gru", hidden_dim=24)
AE3B = AEConfig(model_id="ae3_gru", hidden_dim=32)
AE4 = AEConfig(model_id="ae4_tcn", conv_channels=24, frame_latent_dim=8)
AE5 = AEConfig(model_id="ae5_cnn_gru", conv_channels=24, frame_embed_dim=16, hidden_dim=24, latent_dim=8)
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
        raise ValueError(f"expected [B,N,D], got rank {x.ndim}")
    if x.shape[1] != n_frames or x.shape[2] != d_features:
        raise ValueError(
            f"expected [B,{n_frames},{d_features}], got {tuple(x.shape)}"
        )
```

## AE-0: Linear Tiny AE

Architecture for `N=12`, `D=12`:

```text
[B,12,12] -> flatten [B,144] -> Dense 32 -> Dense 8 ->
Dense 32 -> Dense 144 -> reshape [B,12,12]
```

PyTorch skeleton:

```python
class AE0LinearTiny(nn.Module):
    def __init__(self, cfg: AEConfig):
        super().__init__()
        self.cfg = cfg
        l_in = cfg.n_frames * cfg.d_features
        self.net = nn.Sequential(
            nn.Flatten(),
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

## AE-1: Flat MLP AE

AE-1 uses the same implementation as AE-0 with `hidden_dim=64` and
`latent_dim=16`. It is a capacity check for the flattened Dense family, not a
separate temporal hypothesis.

```python
class AE1FlatMLP(AE0LinearTiny):
    pass
```

## AE-2: Two-Level Dense AE

Architecture for `N=12`, `D=12`, frame code `F=8`, and sequence bottleneck
`z=8`:

```text
[B,12,12] -> TD Dense 16 -> TD Dense 8 -> flatten [B,96] ->
Dense 24 -> Dense 8 -> Dense 24 -> Dense 96 ->
reshape [B,12,8] -> TD Dense 16 -> TD Dense 12 -> [B,12,12]
```

Both compression steps are Dense layers: first per frame, then over the flattened
12-frame pattern.

PyTorch skeleton:

```python
class AE2TwoLevelDense(nn.Module):
    def __init__(self, cfg: AEConfig):
        super().__init__()
        self.cfg = cfg
        f = cfg.frame_latent_dim
        seq_width = cfg.n_frames * f
        self.frame_encoder = nn.Sequential(
            nn.Linear(cfg.d_features, cfg.frame_embed_dim),
            make_activation(cfg.activation),
            nn.Linear(cfg.frame_embed_dim, f),
            make_activation(cfg.activation),
        )
        self.sequence_bottleneck = nn.Sequential(
            nn.Linear(seq_width, cfg.hidden_dim),
            make_activation(cfg.activation),
            nn.Linear(cfg.hidden_dim, cfg.latent_dim),
            make_activation(cfg.activation),
            nn.Linear(cfg.latent_dim, cfg.hidden_dim),
            make_activation(cfg.activation),
            nn.Linear(cfg.hidden_dim, seq_width),
            make_activation(cfg.activation),
        )
        self.frame_decoder = nn.Sequential(
            nn.Linear(f, cfg.frame_embed_dim),
            make_activation(cfg.activation),
            nn.Linear(cfg.frame_embed_dim, cfg.d_features),
        )

    def forward(self, x: Tensor) -> Tensor:
        assert_3d_input(x, self.cfg.n_frames, self.cfg.d_features)
        frame_code = self.frame_encoder(x)
        seq_code = frame_code.reshape(x.shape[0], self.cfg.n_frames * self.cfg.frame_latent_dim)
        seq_recon = self.sequence_bottleneck(seq_code)
        frame_recon = seq_recon.reshape(x.shape[0], self.cfg.n_frames, self.cfg.frame_latent_dim)
        return self.frame_decoder(frame_recon)
```

## AE-3: GRU Contextual AE

Architecture for `N=12`, `D=12`, `H=24`:

```text
[B,12,12] -> GRU context H -> TD Dense z -> TD Dense H ->
GRU decoder H -> TimeDistributed Dense 12 -> [B,12,12]
```

GRU layers provide temporal context. The information-reducing step is the
explicit per-frame Dense bottleneck, not the GRU hidden state.

PyTorch skeleton:

```python
class AE3GRUContextual(nn.Module):
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
        self.bottleneck = nn.Sequential(
            nn.Linear(h, cfg.latent_dim),
            make_activation(cfg.activation),
            nn.Linear(cfg.latent_dim, h),
            make_activation(cfg.activation),
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
        context, _ = self.encoder(x)
        z = self.bottleneck(context)
        dec, _ = self.decoder(z)
        return self.output(dec)
```

## AE-4: Temporal Conv1D AE

Architecture for `N=12`, `D=12`:

```text
[B,12,12] -> Conv1D 24 -> Conv1D 24 -> TD Dense 8 ->
TD Dense 24 -> Conv1D 24 -> Conv1D 12 -> [B,12,12]
```

Conv1D expands each scalar frame sequence into local temporal feature channels.
The only intentional compression step is the per-frame Dense bottleneck.

PyTorch skeleton:

```python
class AE4TemporalConv(nn.Module):
    def __init__(self, cfg: AEConfig):
        super().__init__()
        self.cfg = cfg
        c = cfg.conv_channels
        k = cfg.kernel_size
        p = k // 2
        self.encoder = nn.Sequential(
            nn.Conv1d(cfg.d_features, c, kernel_size=k, padding=p),
            make_activation(cfg.activation),
            nn.Conv1d(c, c, kernel_size=k, padding=p),
            make_activation(cfg.activation),
        )
        self.bottleneck = nn.Sequential(
            nn.Linear(c, cfg.frame_latent_dim),
            make_activation(cfg.activation),
            nn.Linear(cfg.frame_latent_dim, c),
            make_activation(cfg.activation),
        )
        self.decoder = nn.Sequential(
            nn.Conv1d(c, c, kernel_size=k, padding=p),
            make_activation(cfg.activation),
            nn.Conv1d(c, cfg.d_features, kernel_size=k, padding=p),
        )

    def forward(self, x: Tensor) -> Tensor:
        assert_3d_input(x, self.cfg.n_frames, self.cfg.d_features)
        y = x.transpose(1, 2)
        y = self.encoder(y).transpose(1, 2)
        y = self.bottleneck(y)
        y = self.decoder(y.transpose(1, 2))
        return y.transpose(1, 2)
```

## AE-5: Tiny CNN-GRU AE

Use this to test the original CNN-GRU hypothesis after simpler candidates. With
scalar-only inputs, the Conv1D is applied to the fixed `[N,D]` sequence as a
pointwise channel mixer. It must not reshape features into fake histogram
buckets.

For AE-5, `kernel_size=1` is deliberate: the convolution mixes heterogeneous
feature channels within each frame before the GRU sees a denoised frame code.

Architecture for `N=12`, `D=12`, `H=24`:

```text
[B,12,12]
Pointwise Conv1D K=1, 12 -> 24 channels     [B,12,24]
TimeDistributed Dense 24 -> 16              [B,12,16]
GRU temporal context H                       [B,12,H]
TimeDistributed Dense H -> z -> H            [B,12,H]
GRU decoder                                  [B,12,H]
Dense H -> 12 -> linear                      [B,12,12]
```

The pointwise Conv1D mixes heterogeneous scalar feature channels within each
frame. The pre-GRU TimeDistributed Dense layer reduces noisy mixtures into a
macro frame code. GRU attaches temporal context to that code, and the post-GRU
Dense bottleneck selects the most important contextual components.

PyTorch skeleton:

```python
class AE5TinyCNNGRU(nn.Module):
    def __init__(self, cfg: AEConfig):
        super().__init__()
        self.cfg = cfg
        c = cfg.conv_channels
        h = cfg.hidden_dim
        self.temporal_cnn = nn.Sequential(
            nn.Conv1d(cfg.d_features, c, kernel_size=1),
            make_activation(cfg.activation),
        )
        self.frame_code = nn.Sequential(
            nn.Linear(c, cfg.frame_embed_dim),
            make_activation(cfg.activation),
        )
        self.encoder = nn.GRU(
            input_size=cfg.frame_embed_dim,
            hidden_size=h,
            num_layers=1,
            batch_first=True,
        )
        self.bottleneck = nn.Sequential(
            nn.Linear(h, cfg.latent_dim),
            make_activation(cfg.activation),
        )
        self.expansion = nn.Sequential(
            nn.Linear(cfg.latent_dim, h),
            make_activation(cfg.activation),
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
        y = self.temporal_cnn(x.transpose(1, 2)).transpose(1, 2)
        y = self.frame_code(y)
        context, _ = self.encoder(y)
        z = self.bottleneck(context)
        seed = self.expansion(z)
        dec, _ = self.decoder(seed)
        return self.output(dec)
```

Implementation notes:

- This model assumes `D=12` and scalar-only feature slices.
- The `K=1` Conv1D extracts cross-feature interactions inside each 10-second
  frame; it does not look across neighboring frames.
- The pre-GRU Dense layer is the frame denoising / macro-code step.
- The GRU layers model temporal context; they do not collapse the sequence into
  the latent representation.
- The post-GRU Dense bottleneck is the integrated contextual selection step.
- Use only after AE-2, AE-3, and AE-4 establish the quality/memory curve.

## Builder Function

Use one builder entry point so experiment configs can select models by ID:

```python
def build_autoencoder(cfg: AEConfig) -> nn.Module:
    if cfg.model_id == "ae0_linear_tiny":
        return AE0LinearTiny(cfg)
    if cfg.model_id == "ae1_flat_mlp":
        return AE1FlatMLP(cfg)
    if cfg.model_id == "ae2_two_level_dense":
        return AE2TwoLevelDense(cfg)
    if cfg.model_id == "ae3_gru":
        return AE3GRUContextual(cfg)
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
    "intensity": 1.0,
    "write_ratio": 1.0,
    "mean_lba": 1.0,
    "mean_length": 1.0,
    "frame_deltas": 0.5,
    "optional_telemetry": 1.0,
    "padding": 0.0,
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
        if w == 0.0:
            continue
        score = value * w if score is None else score + value * w
        weight_sum += w
    if score is None:
        raise ValueError("at least one feature weight must be nonzero")
    return score / weight_sum


def training_loss(x: Tensor, x_hat: Tensor) -> Tensor:
    return anomaly_score(x, x_hat).mean()
```

For the first implementation, keep the same function for training loss and
offline anomaly score. If optional telemetry becomes available, set its weight
explicitly in the experiment config and record it in the manifest.

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
        input_names=["X"],
        output_names=["X_hat"],
        dynamic_axes=None,
        opset_version=17,
    )
```

Export requirements:

- batch size fixed to 1 for embedded fit studies,
- `N` fixed per exported model,
- `D` fixed to 12 for the scalar contract,
- no thresholding or alert state in the graph,
- parity test compares offline and MNN reconstruction error on identical
  normalized inputs.

## First Verification Checklist

Before claiming any candidate fits:

- parameter count matches the memo,
- dummy forward returns `[1, N, 12]`,
- training loss ignores unavailable optional telemetry and padding,
- ONNX export succeeds with fixed shape,
- MNN conversion succeeds,
- offline and MNN scores match within a documented tolerance,
- model weights plus retained input statistics/state fit inside the 500 KB
  per-volume detector-data budget,
- transient tensors, operator workspace, and reusable inference slots are
  measured separately,
- the target many-volume schedule records how many scratch slots are allocated
  concurrently and still completes every 10-second cadence.
