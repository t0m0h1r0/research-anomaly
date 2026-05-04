from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rad_ae.models import NumpyMLPAEConfig, NumpyMLPAutoEncoder


class NumpyAutoEncoderTest(unittest.TestCase):
    def test_scores_shifted_inputs_higher_than_training_cluster(self) -> None:
        rng = np.random.default_rng(7)
        train = rng.normal(0.0, 0.05, size=(64, 12)).astype(np.float32)
        shifted = rng.normal(2.0, 0.05, size=(16, 12)).astype(np.float32)

        model = NumpyMLPAutoEncoder(
            NumpyMLPAEConfig(input_dim=12, latent_dim=4, epochs=20, batch_size=16, learning_rate=0.01, seed=7)
        ).fit(train)

        train_score = model.score(train)
        shifted_score = model.score(shifted)
        self.assertGreater(float(np.median(shifted_score)), float(np.median(train_score)))
        self.assertGreater(model.parameter_count, 0)


if __name__ == "__main__":
    unittest.main()
