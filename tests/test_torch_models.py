from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rad_ae.torch_models import (  # noqa: E402
    TorchAEConfig,
    build_torch_autoencoder,
    count_torch_parameters,
    require_torch,
)


class TorchModelShapeTest(unittest.TestCase):
    def setUp(self) -> None:
        try:
            self.torch, _nn = require_torch()
        except RuntimeError as exc:
            self.skipTest(str(exc))

    def test_two_level_dense_ae_preserves_sequence_shape(self) -> None:
        cfg = TorchAEConfig(model_type="two_level_dense", sequence_length=12, d_features=12)
        model = build_torch_autoencoder(cfg)
        x = self.torch.zeros(2, 12, 12)
        y = model(x)

        self.assertEqual(tuple(y.shape), (2, 12, 12))
        self.assertEqual(count_torch_parameters(model), 5836)

    def test_gru_contextual_ae_preserves_sequence_shape(self) -> None:
        cfg = TorchAEConfig(model_type="gru", sequence_length=12, d_features=12)
        model = build_torch_autoencoder(cfg)
        x = self.torch.zeros(2, 12, 12)
        y = model(x)

        self.assertEqual(tuple(y.shape), (2, 12, 12))
        self.assertEqual(count_torch_parameters(model), 7052)

    def test_temporal_conv_ae_preserves_sequence_shape(self) -> None:
        cfg = TorchAEConfig(model_type="tcn", sequence_length=12, d_features=12)
        model = build_torch_autoencoder(cfg)
        x = self.torch.zeros(2, 12, 12)
        y = model(x)

        self.assertEqual(tuple(y.shape), (2, 12, 12))
        self.assertEqual(count_torch_parameters(model), 5684)

    def test_cnn_gru_contextual_ae_preserves_sequence_shape(self) -> None:
        cfg = TorchAEConfig(model_type="cnn_gru", sequence_length=12, d_features=12)
        model = build_torch_autoencoder(cfg)
        x = self.torch.zeros(2, 12, 12)
        y = model(x)

        self.assertEqual(tuple(y.shape), (2, 12, 12))
        self.assertEqual(count_torch_parameters(model), 8804)


if __name__ == "__main__":
    unittest.main()
