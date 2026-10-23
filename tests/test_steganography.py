"""Unit tests for LSB image steganography module."""

import importlib
import unittest

from PIL import Image

stegno = importlib.import_module("stegno code")


class TestSteganography(unittest.TestCase):
    """Test bit-level LSB steganography encoding and decoding."""

    def test_gen_data(self):
        """Verify binary 8-bit formatting of string characters."""
        data = "AB"
        binary = stegno.genData(data)
        self.assertEqual(binary, ["01000001", "01000010"])

    def test_encode_and_decode_roundtrip(self):
        """Verify that text can be encoded into an image and accurately recovered."""
        payload = "Armadillo Quantum-Safe Payload 2026"
        base_image = Image.new("RGB", (120, 120), color=(100, 150, 200))

        encoded_image = stegno.encode_image(base_image, payload)
        recovered_text = stegno.decode_image(encoded_image)

        self.assertEqual(recovered_text, payload)

    def test_empty_payload_validation(self):
        """Verify that attempting to encode empty payload raises ValueError."""
        base_image = Image.new("RGB", (50, 50), color=(50, 50, 50))
        with self.assertRaises(ValueError):
            stegno.encode_image(base_image, "")

    def test_symbols_and_numbers(self):
        """Verify payload containing whitespace, special characters, and digits."""
        payload = "Token: #1234-XYZ! (ML-KEM-768 & X25519) -> 100%"
        base_image = Image.new("RGB", (150, 150), color=(20, 30, 40))

        encoded_image = stegno.encode_image(base_image, payload)
        recovered_text = stegno.decode_image(encoded_image)

        self.assertEqual(recovered_text, payload)


if __name__ == "__main__":
    unittest.main()
