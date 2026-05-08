"""Image LSB steganography implementation."""

import numpy as np
from PIL import Image
import io
from .crypto import encrypt_message, decrypt_message


def calculate_capacity(image):
    """Calculate maximum message capacity in bytes."""
    width, height = image.size
    return (width * height * 3) // 8


def encode_image(image_bytes, message, password=None):
    """
    Encode a message into an image using LSB steganography.
    
    Args:
        image_bytes: Raw image data (PNG/BMP)
        message: String message to encode
        password: Optional password for encryption
        
    Returns:
        tuple: (encoded_image_bytes, metadata_dict)
    """
    # Open image
    img = Image.open(io.BytesIO(image_bytes))
    
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Encrypt message if password provided
    if password:
        message_bytes = encrypt_message(message.encode('utf-8'), password)
        is_encrypted = True
    else:
        message_bytes = message.encode('utf-8')
        is_encrypted = False
    
    # Check capacity
    max_capacity = calculate_capacity(img)
    if len(message_bytes) + 4 > max_capacity:
        raise ValueError(f"Message too large. Max capacity: {max_capacity} bytes, "
                        f"Message size: {len(message_bytes)} bytes")
    
    # Convert image to numpy array
    img_array = np.array(img)
    height, width, channels = img_array.shape
    
    # Prepare binary data: 32-bit length header + message
    length = len(message_bytes)
    binary_data = format(length, '032b') + ''.join(format(byte, '08b') for byte in message_bytes)
    
    # Flatten image array for easier manipulation
    flat_img = img_array.reshape(-1)
    
    # Encode bits into LSB of pixels
    for i, bit in enumerate(binary_data):
        # Clear LSB and set to our bit
        flat_img[i] = (flat_img[i] & 0xFE) | int(bit)
    
    # Reshape back to image dimensions
    encoded_array = flat_img.reshape(height, width, channels)
    
    # Convert back to PIL Image
    encoded_img = Image.fromarray(encoded_array.astype(np.uint8))
    
    # Save to bytes
    output = io.BytesIO()
    encoded_img.save(output, format='PNG')
    output.seek(0)
    
    metadata = {
        'original_size': img.size,
        'message_length': length,
        'encrypted': is_encrypted,
        'capacity_used': f"{(length + 4) / max_capacity * 100:.1f}%"
    }
    
    return output.getvalue(), metadata


def decode_image(image_bytes, password=None):
    """
    Decode a message from an image using LSB steganography.
    
    Args:
        image_bytes: Raw image data
        password: Optional password for decryption
        
    Returns:
        tuple: (decoded_message, metadata_dict)
    """
    # Open image
    img = Image.open(io.BytesIO(image_bytes))
    
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Convert to numpy array
    img_array = np.array(img)
    
    # Flatten array
    flat_img = img_array.reshape(-1)
    
    # Extract LSBs
    bits = [str(pixel & 1) for pixel in flat_img]
    
    # Extract length (first 32 bits)
    length_bits = ''.join(bits[:32])
    message_length = int(length_bits, 2)
    
    if message_length <= 0 or message_length > len(flat_img) // 8:
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
