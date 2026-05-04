from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rad_ae.features import FeatureConfig, RobustNormalizer, build_frames, make_sequences
from rad_ae.ransap import discover_trace_sources, read_trace_events


class FeaturePipelineTest(unittest.TestCase):
    def test_discovers_and_builds_ransap_style_sequences(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run = root / "original" / "win7-120gb-hdd" / "benign_chrome_001"
            run.mkdir(parents=True)
            (run / "ata_read.csv").write_text(
                "100,0,0,4096\n110,0,8,4096\n120,0,16,4096\n",
                encoding="utf-8",
            )
            (run / "ata_write.csv").write_text(
                "105,0,32,4096,0.2,0.1\n115,0,40,8192,0.3,0.2\n",
                encoding="utf-8",
            )

            sources = discover_trace_sources(root)
            self.assertEqual(len(sources), 1)
            self.assertEqual(sources[0].label, "benign")

            events = read_trace_events(sources[0])
            result = build_frames(events, FeatureConfig(sequence_length=2))
            sequences = make_sequences(result.frames, sequence_length=2, stride=1)

            self.assertEqual(result.event_count, 5)
            self.assertEqual(result.entropy_event_count, 2)
            self.assertEqual(sequences.shape[1:], (2, 12))
            self.assertGreater(float(sequences[..., 1].max()), 0.0)
            self.assertGreater(float(sequences[..., 3].max()), 0.0)

    def test_normalizer_round_trip_shape(self) -> None:
        x = np.arange(2 * 3 * 12, dtype=np.float32).reshape(2, 3, 12)
        normalizer = RobustNormalizer().fit(x)
        transformed = normalizer.transform(x)
        self.assertEqual(transformed.shape, x.shape)
        self.assertTrue(np.isfinite(transformed).all())


if __name__ == "__main__":
    unittest.main()
