import sys
import unittest
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from action_fx import action_fx, strong_spell_fx


class ActionFXTests(unittest.TestCase):
    def setUp(self):
        self.frame = Image.new("RGB", (160, 90), (30, 40, 50))
        self.empty = Image.new("L", self.frame.size, 0)

    def test_empty_mask_preserves_pixels(self):
        for effect in (action_fx, strong_spell_fx):
            np.testing.assert_array_equal(effect(self.frame, self.empty), self.frame)

    def test_aura_is_local_and_changes_subject_region(self):
        mask = self.empty.copy()
        ImageDraw.Draw(mask).rectangle((65, 30, 95, 60), fill=255)
        output = np.asarray(action_fx(self.frame, mask))
        original = np.asarray(self.frame)
        np.testing.assert_array_equal(output[0, 0], original[0, 0])
        self.assertTrue(np.any(output[25:65, 60:100] != original[25:65, 60:100]))

    def test_invalid_mask_dimensions_rejected(self):
        for effect in (action_fx, strong_spell_fx):
            with self.assertRaises(ValueError):
                effect(self.frame, Image.new("L", (10, 10)))

    def test_beam_is_repeatable_and_visible_at_endpoint(self):
        kwargs = dict(beam=((.2, .5), (.8, .5), 1), seed=42)
        first = strong_spell_fx(self.frame, self.empty, **kwargs)
        second = strong_spell_fx(self.frame, self.empty, **kwargs)
        np.testing.assert_array_equal(first, second)
        self.assertGreater(int(np.asarray(first)[45, 128].sum()), 120)


if __name__ == "__main__":
    unittest.main()
