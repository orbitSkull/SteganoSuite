"""Steganalysis tools for detecting hidden data."""

import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64


def chi_square_analysis(image_bytes):
    """
    Perform chi-square statistical attack to detect LSB embedding.
    
    Args:
        image_bytes: Raw image data
        
    Returns:
        dict: Analysis results with confidence score
    """
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    img_array = np.array(img)
    
    # Analyze each channel separately
    scores = []
    for channel in range(3):  # R, G, B
        channel_data = img_array[:, :, channel].flatten()
        
        # Create pairs of adjacent values (2k, 2k+1)
        hist = np.bincount(channel_data, minlength=256)
        
        chi_sq = 0.0
        used_pairs = 0
        
        for i in range(0, 256, 2):
            observed_0 = hist[i]      # Even values
            observed_1 = hist[i + 1]  # Odd values
            
            expected = (observed_0 + observed_1) / 2.0
            
            if expected > 0:
                chi_sq += ((observed_0 - expected) ** 2 + (observed_1 - expected) ** 2) / expected
                used_pairs += 1
        
        # Normalize score (higher chi-square = more likely to be clean)
        # Lower chi-square = more uniform distribution = likely stego
        if used_pairs > 0:
            scores.append(chi_sq / used_pairs)
    
    # Average score across channels
    avg_score = np.mean(scores) if scores else 0
    
    # Convert to confidence percentage (higher = more suspicious)
    # Chi-square values typically range from 0 to 1000+
    # Normalize to 0-100 scale
    confidence = min(100, max(0, 100 - avg_score / 10))
    
    # Determine verdict
    if confidence > 70:
        verdict = "Likely Contains Hidden Data"
        verdict_class = "danger"
    elif confidence > 40:
        verdict = "Suspicious"
        verdict_class = "warning"
    else:
        verdict = "Clean"
        verdict_class = "success"
    
    return {
        'chi_square_score': round(avg_score, 2),
        'confidence': round(confidence, 1),
        'verdict': verdict,
        'verdict_class': verdict_class
    }


def generate_histogram_comparison(image_bytes):
    """
    Generate histogram comparison chart for RGB channels.
    
    Args:
        image_bytes: Raw image data
        
    Returns:
        str: Base64 encoded PNG image
    """
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    img_array = np.array(img)
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    colors = ['red', 'green', 'blue']
    labels = ['Red Channel', 'Green Channel', 'Blue Channel']
    
    for i, (ax, color, label) in enumerate(zip(axes, colors, labels)):
        channel_data = img_array[:, :, i].flatten()
        ax.hist(channel_data, bins=256, color=color, alpha=0.7, range=(0, 256))
        ax.set_xlabel('Pixel Value')
        ax.set_ylabel('Frequency')
        ax.set_title(label)
        ax.set_xlim(0, 255)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save to buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def generate_bit_planes(image_bytes):
    """
    Generate bit-plane visualization for the image.
    
    Args:
        image_bytes: Raw image data
        
    Returns:
        str: Base64 encoded PNG image showing all bit planes
    """
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    img_array = np.array(img)
    
    # Get dimensions
    height, width, _ = img_array.shape
    
    # Create bit planes for each channel (8 bits per channel)
    fig, axes = plt.subplots(3, 8, figsize=(16, 6))
    
    for channel in range(3):
        channel_data = img_array[:, :, channel]
        
        for bit in range(8):
            # Extract bit plane
            bit_plane = ((channel_data >> bit) & 1) * 255
            
            ax = axes[channel, bit]
            ax.imshow(bit_plane, cmap='gray', vmin=0, vmax=255)
            ax.set_title(f'Bit {bit}')
            ax.axis('off')
    
    # Add row labels
    axes[0, 0].set_ylabel('Red', fontsize=12, rotation=0, ha='right', va='center')
    axes[1, 0].set_ylabel('Green', fontsize=12, rotation=0, ha='right', va='center')
    axes[2, 0].set_ylabel('Blue', fontsize=12, rotation=0, ha='right', va='center')
    
    plt.tight_layout()
    
    # Save to buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def analyze_image(image_bytes):
    """
    Perform complete steganalysis on an image.
    
    Args:
        image_bytes: Raw image data
        
    Returns:
        dict: Complete analysis results
    """
    chi_results = chi_square_analysis(image_bytes)
    histogram_b64 = generate_histogram_comparison(image_bytes)
    bit_planes_b64 = generate_bit_planes(image_bytes)
    
    return {
        **chi_results,
        'histogram_image': histogram_b64,
        'bit_planes_image': bit_planes_b64
    }
