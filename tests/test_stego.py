"""Unit tests for SteganoSuite steganography modules."""

import pytest
import io
import os
from PIL import Image
import numpy as np
import wave

from stego.image_stego import encode_image, decode_image, calculate_capacity
from stego.audio_stego import encode_audio, decode_audio
from stego.text_stego import encode_text, decode_text, clean_text
from stego.crypto import encrypt_message, decrypt_message


# Test fixtures
@pytest.fixture
def test_image():
    """Create a simple test image."""
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes.getvalue()


@pytest.fixture
def test_audio():
    """Create a simple test WAV audio file."""
    output = io.BytesIO()
    
    # Create 1 second of 16-bit PCM audio at 44100 Hz
    sample_rate = 44100
    duration = 1
    num_samples = sample_rate * duration
    
    # Generate sine wave
    t = np.linspace(0, duration, num_samples)
    audio_data = (np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
    
    wav_file = wave.open(output, 'wb')
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)
    wav_file.writeframes(audio_data.tobytes())
    wav_file.close()
    
    output.seek(0)
    return output.getvalue()


# Image Steganography Tests
class TestImageSteganography:
    
    def test_image_encode_decode_roundtrip(self, test_image):
        """Test basic encode/decode roundtrip."""
        message = "Hello, SteganoSuite!"
        
        encoded_bytes, metadata = encode_image(test_image, message)
        assert metadata['encrypted'] == False
        
        decoded_message, decode_metadata = decode_image(encoded_bytes)
        assert decoded_message == message
    
    def test_image_encode_with_encryption(self, test_image):
        """Test encode/decode with encryption."""
        message = "Secret encrypted message"
        password = "mypassword123"
        
        encoded_bytes, metadata = encode_image(test_image, message, password)
        assert metadata['encrypted'] == True
        
        decoded_message, _ = decode_image(encoded_bytes, password)
        assert decoded_message == message
    
    def test_image_wrong_password(self, test_image):
        """Test decoding with wrong password raises error."""
        message = "Secret message"
        password = "correctpassword"
        wrong_password = "wrongpassword"
        
        encoded_bytes, _ = encode_image(test_image, message, password)
        
        with pytest.raises(ValueError):
            decode_image(encoded_bytes, wrong_password)
    
    def test_image_capacity_check(self, test_image):
        """Test capacity check for large messages."""
        # Calculate max capacity
        img = Image.open(io.BytesIO(test_image))
        max_capacity = calculate_capacity(img)
        
        # Try to encode a message that's too large
        large_message = "A" * (max_capacity + 100)
        
        with pytest.raises(ValueError) as exc_info:
            encode_image(test_image, large_message)
        
        assert "too large" in str(exc_info.value).lower()


# Audio Steganography Tests
class TestAudioSteganography:
    
    def test_audio_encode_decode_roundtrip(self, test_audio):
        """Test basic audio encode/decode roundtrip."""
        message = "Hidden in audio!"
        
        encoded_bytes, metadata = encode_audio(test_audio, message)
        assert metadata['encrypted'] == False
        
        decoded_message, _ = decode_audio(encoded_bytes)
        assert decoded_message == message
    
    def test_audio_encode_with_encryption(self, test_audio):
        """Test audio encode/decode with encryption."""
        message = "Secret audio message"
        password = "audiopass456"
        
        encoded_bytes, metadata = encode_audio(test_audio, message, password)
        assert metadata['encrypted'] == True
        
        decoded_message, _ = decode_audio(encoded_bytes, password)
        assert decoded_message == message
    
    def test_audio_wrong_password(self, test_audio):
        """Test audio decoding with wrong password."""
        message = "Secret audio"
        password = "correct"
        wrong_password = "wrong"
        
        encoded_bytes, _ = encode_audio(test_audio, message, password)
        
        with pytest.raises(ValueError):
            decode_audio(encoded_bytes, wrong_password)


# Text Steganography Tests
class TestTextSteganography:
    
    def test_text_encode_decode_roundtrip(self):
        """Test basic text encode/decode roundtrip."""
        cover_text = "This is a normal looking message that contains hidden data."
        secret_message = "Secret data here!"
        
        stego_text = encode_text(cover_text, secret_message)
        
        # Verify we can decode it
        decoded = decode_text(stego_text)
        assert decoded == secret_message
    
    def test_text_invisible_characters(self):
        """Test that stego text looks normal when zero-width chars are stripped."""
        cover_text = "Hello World this is a test"
        secret_message = "Hidden message"
        
        stego_text = encode_text(cover_text, secret_message)
        
        # Clean the stego text
        cleaned = clean_text(stego_text)
        
        # The cleaned text should look like the original
        # (may not be exact due to distribution of characters)
        assert len(cleaned) > 0
        assert all(c != '\u200b' and c != '\u200c' for c in cleaned)


# Encryption Tests
class TestEncryption:
    
    def test_crypto_encrypt_decrypt(self):
        """Test basic encryption/decryption roundtrip."""
        plaintext = b"Hello, World!"
        password = "testpassword"
        
        ciphertext = encrypt_message(plaintext, password)
        decrypted = decrypt_message(ciphertext, password)
        
        assert decrypted == plaintext
    
    def test_crypto_wrong_password(self):
        """Test decryption with wrong password raises error."""
        plaintext = b"Secret message"
        password = "correct"
        wrong_password = "wrong"
        
        ciphertext = encrypt_message(plaintext, password)
        
        with pytest.raises(Exception):
            decrypt_message(ciphertext, wrong_password)
    
    def test_crypto_different_ciphertexts(self):
        """Test that encrypting same plaintext twice gives different ciphertexts (due to salt)."""
        plaintext = b"Test message"
        password = "password"
        
        ciphertext1 = encrypt_message(plaintext, password)
        ciphertext2 = encrypt_message(plaintext, password)
        
        # Should be different due to random salt
        assert ciphertext1 != ciphertext2
        
        # But both should decrypt to same plaintext
        assert decrypt_message(ciphertext1, password) == plaintext
        assert decrypt_message(ciphertext2, password) == plaintext


# Integration Tests
class TestIntegration:
    
    def test_full_image_workflow(self, test_image):
        """Test complete image steganography workflow with encryption."""
        original_message = "This is a comprehensive test message with special chars: !@#$%^&*()"
        password = "secure_password_123"
        
        # Encode
        encoded_bytes, encode_metadata = encode_image(test_image, original_message, password)
        assert encode_metadata['encrypted'] == True
        
        # Decode
        decoded_message, decode_metadata = decode_image(encoded_bytes, password)
        assert decode_metadata['encrypted'] == True
        assert decoded_message == original_message
    
    def test_text_steganography_preserves_appearance(self):
        """Test that text steganography preserves the appearance of cover text."""
        cover_text = """Dear Team,

I wanted to share some important updates about our project.
We have made significant progress and are on track.

Best regards,
John"""
        
        secret_message = "Q2: Revenue up 25%, New product launch next month"
        
        stego_text = encode_text(cover_text, secret_message)
        
        # The visible text should still make sense
        cleaned = clean_text(stego_text)
        assert len(cleaned.split()) >= len(cover_text.split()) - 2  # Allow some variation


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
