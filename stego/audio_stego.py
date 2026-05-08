"""Audio WAV LSB steganography implementation."""

import wave
import io
import numpy as np
from .crypto import encrypt_message, decrypt_message


def encode_audio(audio_bytes, message, password=None):
    """
    Encode a message into a WAV audio file using LSB steganography.
    
    Args:
        audio_bytes: Raw WAV file data
        message: String message to encode
        password: Optional password for encryption
        
    Returns:
        tuple: (encoded_audio_bytes, metadata_dict)
    """
    # Read WAV file
    wav_in = wave.open(io.BytesIO(audio_bytes), 'rb')
    
    # Get audio parameters
    n_channels = wav_in.getnchannels()
    sample_width = wav_in.getsampwidth()
    frame_rate = wav_in.getframerate()
    n_frames = wav_in.getnframes()
    
    # Only support 16-bit PCM
    if sample_width != 2:
        raise ValueError("Only 16-bit PCM WAV files are supported")
    
    # Read all frames
    frames = wav_in.readframes(n_frames)
    wav_in.close()
    
    # Convert to numpy array
    audio_array = np.frombuffer(frames, dtype=np.int16)
    
    # Encrypt message if password provided
    if password:
        message_bytes = encrypt_message(message.encode('utf-8'), password)
        is_encrypted = True
    else:
        message_bytes = message.encode('utf-8')
        is_encrypted = False
    
    # Check capacity (1 bit per sample)
    max_capacity = len(audio_array) // 8
    if len(message_bytes) + 4 > max_capacity:
        raise ValueError(f"Message too large. Max capacity: {max_capacity} bytes")
    
    # Prepare binary data: 32-bit length header + message
    length = len(message_bytes)
    binary_data = format(length, '032b') + ''.join(format(byte, '08b') for byte in message_bytes)
    
    encoded_array = audio_array.copy().astype(np.uint16)
    
    for i, bit in enumerate(binary_data):
        encoded_array[i] = (encoded_array[i] & 0xFFFE) | int(bit)
    
    encoded_array = encoded_array.astype(np.int16)
    
    # Create output WAV file
    output = io.BytesIO()
    wav_out = wave.open(output, 'wb')
    wav_out.setnchannels(n_channels)
    wav_out.setsampwidth(sample_width)
    wav_out.setframerate(frame_rate)
    wav_out.writeframes(encoded_array.astype(np.int16).tobytes())
    wav_out.close()
    
    output.seek(0)
    
    metadata = {
        'duration': n_frames / frame_rate,
        'sample_rate': frame_rate,
        'channels': n_channels,
        'message_length': length,
        'encrypted': is_encrypted
    }
    
    return output.getvalue(), metadata


def decode_audio(audio_bytes, password=None):
    """
    Decode a message from a WAV audio file using LSB steganography.
    
    Args:
        audio_bytes: Raw WAV file data
        password: Optional password for decryption
        
    Returns:
        tuple: (decoded_message, metadata_dict)
    """
    # Read WAV file
    wav_in = wave.open(io.BytesIO(audio_bytes), 'rb')
    
    # Get parameters
    sample_width = wav_in.getsampwidth()
    n_frames = wav_in.getnframes()
    
    # Only support 16-bit PCM
    if sample_width != 2:
        raise ValueError("Only 16-bit PCM WAV files are supported")
    
    # Read frames
    frames = wav_in.readframes(n_frames)
    wav_in.close()
    
    # Convert to numpy array
    audio_array = np.frombuffer(frames, dtype=np.int16)
    
    # Extract LSBs
    bits = [str(sample & 1) for sample in audio_array]
    
    # Extract length (first 32 bits)
    length_bits = ''.join(bits[:32])
    message_length = int(length_bits, 2)
    
    if message_length <= 0 or message_length > len(audio_array) // 8:
        raise ValueError("Invalid message length or no hidden message found")
    
    # Extract message bits
    message_bits = ''.join(bits[32:32 + message_length * 8])
    
    # Convert bits to bytes
    message_bytes = bytes(int(message_bits[i:i+8], 2) for i in range(0, len(message_bits), 8))
    
    # Decrypt if password provided
    if password:
        try:
            message_bytes = decrypt_message(message_bytes, password)
            is_encrypted = True
        except Exception:
            raise ValueError("Failed to decrypt. Wrong password or corrupted data.")
    else:
        is_encrypted = False
    
    # Decode to string
    try:
        message = message_bytes.decode('utf-8')
    except UnicodeDecodeError:
        raise ValueError("Failed to decode message. It may be encrypted or corrupted.")
    
    metadata = {
        'message_length': message_length,
        'encrypted': is_encrypted
    }
    
    return message, metadata
