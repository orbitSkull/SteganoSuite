"""File format conversion utilities for steganography."""

import io
from PIL import Image
import numpy as np

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False


def convert_image_to_png(image_bytes):
    """
    Convert any image format to PNG for steganography processing.
    
    Args:
        image_bytes: Raw image data (JPEG, WebP, BMP, etc.)
        
    Returns:
        bytes: PNG formatted image data
        
    Raises:
        ValueError: If conversion fails
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary (handles RGBA, P mode, etc.)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save as PNG
        output = io.BytesIO()
        img.save(output, format='PNG', optimize=True)
        output.seek(0)
        
        return output.getvalue()
        
    except Exception as e:
        raise ValueError(f"Failed to convert image to PNG: {str(e)}")


def convert_audio_to_wav(audio_bytes, original_format=None):
    """
    Convert any audio format to WAV (16-bit PCM) for steganography processing.
    
    Args:
        audio_bytes: Raw audio data (MP3, AAC, FLAC, etc.)
        original_format: Original file format extension (e.g., 'mp3', 'flac')
        
    Returns:
        bytes: WAV formatted audio data (16-bit PCM)
        
    Raises:
        ValueError: If conversion fails or pydub is not available
    """
    if not PYDUB_AVAILABLE:
        raise ValueError("Audio conversion requires pydub. Install with: pip install pydub")
    
    try:
        # Load audio from bytes
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format=original_format)
        
        # Convert to mono if stereo (for better capacity calculation)
        if audio.channels > 1:
            audio = audio.set_channels(1)
        
        # Convert to 16-bit PCM
        audio = audio.set_sample_width(2)
        
        # Convert to 44.1kHz sample rate (standard)
        if audio.frame_rate != 44100:
            audio = audio.set_frame_rate(44100)
        
        # Export as WAV
        output = io.BytesIO()
        audio.export(output, format='wav')
        output.seek(0)
        
        return output.getvalue()
        
    except Exception as e:
        raise ValueError(f"Failed to convert audio to WAV: {str(e)}")


def get_image_info(image_bytes):
    """
    Get information about an image without converting.
    
    Args:
        image_bytes: Raw image data
        
    Returns:
        dict: Image information (format, size, mode)
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        return {
            'format': img.format,
            'size': img.size,
            'mode': img.mode,
            'width': img.width,
            'height': img.height
        }
    except Exception:
        return None


def is_lossless_format(filename):
    """
    Check if an image format is lossless (PNG, BMP, TIFF).
    
    Args:
        filename: Filename to check
        
    Returns:
        bool: True if lossless, False otherwise
    """
    lossless_extensions = {'.png', '.bmp', '.tiff', '.tif'}
    ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext in lossless_extensions


def warn_if_lossy(filename):
    """
    Check if file is a lossy format and return a warning message.
    
    Args:
        filename: Filename to check
        
    Returns:
        str or None: Warning message if lossy, None if lossless
    """
    lossy_extensions = {'.jpg', '.jpeg', '.webp'}
    ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    
    if ext in {'.jpg', '.jpeg'}:
        return "JPEG detected. The image will be converted to PNG (lossless) for steganography."
    elif ext == '.webp':
        return "WebP detected. The image will be converted to PNG (lossless) for steganography."
    
    return None
