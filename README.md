# SteganoSuite

A comprehensive, professional-grade steganography web platform built with Python Flask. Hide secret messages in images, audio, and text files with military-grade AES-256 encryption.

## Features

- **Image Steganography**: Hide messages in images using LSB (Least Significant Bit) encoding
  - Supported formats: PNG, JPG, JPEG, WebP, BMP (auto-converts to PNG)
- **Audio Steganography**: Embed data in audio files without affecting sound quality
  - Supported formats: WAV, MP3, FLAC, AAC, OGG, M4A (auto-converts to 16-bit PCM WAV)
- **Text Steganography**: Conceal messages using invisible zero-width Unicode characters
- **AES-256 Encryption**: Optional password-based encryption for all data types
- **Steganalysis Tools**: Detect hidden messages with chi-square analysis, histograms, and bit-plane visualization
- **Modern Web UI**: Dark glassmorphism theme with drag-and-drop support
- **File Conversion**: Automatic conversion of uploaded files to optimal formats for steganography

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. **For Audio Support** (Optional but recommended):
   - Install ffmpeg for audio file conversion (MP3, FLAC, etc.):
     - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
     - **Mac**: `brew install ffmpeg`
     - **Linux**: `sudo apt-get install ffmpeg`

3. Run the application:
```bash
python app.py
```

4. Open browser: http://localhost:5000

## Usage

### Image Steganography
- Upload any image (PNG, JPG, WebP, BMP)
- System auto-converts to PNG for lossless steganography
- Enter your secret message
- Optionally add AES-256 encryption password
- Download the stego image (always in PNG format)

### Audio Steganography
- Upload any audio file (WAV, MP3, FLAC, AAC, OGG, M4A)
- System auto-converts to 16-bit PCM WAV
- Enter your secret message
- Optionally add encryption password
- Download the stego audio (always in WAV format)

### Text Steganography
- Enter cover text (visible message)
- Enter secret message to hide
- System embeds using invisible zero-width Unicode characters
- Copy and share the stego text

### Steganalysis
- Upload any image (all formats supported)
- View statistical analysis results
- Check histograms and bit-plane visualizations
- Get confidence score for hidden data detection

## Supported File Formats

### Input Formats
- **Images**: PNG, JPG, JPEG, WebP, BMP
- **Audio**: WAV, MP3, FLAC, AAC, OGG, M4A
- **Output**: Always PNG for images, WAV for audio

### Notes
- JPEG and WebP images are converted to PNG before processing
- Non-WAV audio files are converted to 16-bit PCM WAV
- Output files are always in the optimal format for steganography

## Testing

```bash
python -m pytest tests/ -v
```

## Tech Stack

- Flask 3.x, Jinja2, vanilla CSS/JS
- AES-256-GCM encryption (PBKDF2 with 100k iterations)
- PIL/Pillow, NumPy, Matplotlib
- pydub for audio file conversion
- ffmpeg (external dependency for audio processing)
