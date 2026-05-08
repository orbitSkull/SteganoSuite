"""Flask application for SteganoSuite."""

import os
import uuid
import io
import base64
from flask import Flask, render_template, request, send_file, flash, redirect, url_for, jsonify
from werkzeug.utils import secure_filename

from config import Config
from stego.image_stego import encode_image, decode_image
from stego.audio_stego import encode_audio, decode_audio
from stego.text_stego import encode_text, decode_text
from stego.analysis import analyze_image
from stego.converter import (
    convert_image_to_png, convert_audio_to_wav,
    warn_if_lossy, PYDUB_AVAILABLE
)

app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)


def allowed_file(filename, file_type):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS.get(file_type, set())


def save_uploaded_file(file):
    """Save uploaded file and return path."""
    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4()}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
    file.save(filepath)
    return filepath, unique_name


@app.route('/')
def index():
    """Dashboard landing page."""
    return render_template('index.html')


@app.route('/image')
def image():
    """Image steganography page."""
    return render_template('image.html')


@app.route('/image/encode', methods=['POST'])
def image_encode():
    """Encode message into image."""
    if 'image' not in request.files:
        flash('No image file provided', 'error')
        return redirect(url_for('image'))
    
    file = request.files['image']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('image'))
    
    if not allowed_file(file.filename, 'image'):
        flash('Invalid file type. Please upload PNG, JPG, WebP, or BMP.', 'error')
        return redirect(url_for('image'))
    
    message = request.form.get('message', '')
    if not message:
        flash('No message provided', 'error')
        return redirect(url_for('image'))
    
    password = request.form.get('password') or None
    
    try:
        image_bytes = file.read()
        original_filename = file.filename.lower()
        
        # Check for lossy format warning
        warning_msg = warn_if_lossy(original_filename)
        if warning_msg:
            flash(warning_msg, 'warning')
        
        # Convert to PNG if needed
        if not original_filename.endswith(('.png', '.bmp')):
            image_bytes = convert_image_to_png(image_bytes)
            flash(f"Converted {original_filename.rsplit('.', 1)[-1].upper()} to PNG for processing", 'info')
        
        encoded_bytes, metadata = encode_image(image_bytes, message, password)
        
        # Save output file
        output_filename = f"stego_{uuid.uuid4()}.png"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        with open(output_path, 'wb') as f:
            f.write(encoded_bytes)
        
        # Create preview
        preview_b64 = base64.b64encode(encoded_bytes).decode('utf-8')
        
        flash(f"Message encoded successfully! Capacity used: {metadata['capacity_used']}", 'success')
        return render_template('image.html', 
                               download_file=output_filename,
                               preview_image=preview_b64,
                               metadata=metadata)
    
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('image'))
    except Exception as e:
        flash(f'Error encoding image: {str(e)}', 'error')
        return redirect(url_for('image'))


@app.route('/image/decode', methods=['POST'])
def image_decode():
    """Decode message from image."""
    if 'image' not in request.files:
        flash('No image file provided', 'error')
        return redirect(url_for('image'))
    
    file = request.files['image']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('image'))
    
    password = request.form.get('password') or None
    
    try:
        image_bytes = file.read()
        message, metadata = decode_image(image_bytes, password)
        
        flash('Message decoded successfully!', 'success')
        return render_template('image.html', 
                               decoded_message=message,
                               decode_metadata=metadata,
                               active_tab='decode')
    
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('image'))
    except Exception as e:
        flash(f'Error decoding image: {str(e)}', 'error')
        return redirect(url_for('image'))


@app.route('/audio')
def audio():
    """Audio steganography page."""
    return render_template('audio.html')


@app.route('/audio/encode', methods=['POST'])
def audio_encode():
    """Encode message into audio."""
    if 'audio' not in request.files:
        flash('No audio file provided', 'error')
        return redirect(url_for('audio'))
    
    file = request.files['audio']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('audio'))
    
    if not allowed_file(file.filename, 'audio'):
        flash('Invalid file type. Please upload WAV, MP3, FLAC, AAC, OGG, or M4A.', 'error')
        return redirect(url_for('audio'))
    
    message = request.form.get('message', '')
    if not message:
        flash('No message provided', 'error')
        return redirect(url_for('audio'))
    
    password = request.form.get('password') or None
    
    try:
        audio_bytes = file.read()
        original_filename = file.filename.lower()
        
        # Convert to WAV if needed
        if not original_filename.endswith('.wav'):
            if not PYDUB_AVAILABLE:
                flash('Audio conversion requires pydub. Install with: pip install pydub', 'error')
                return redirect(url_for('audio'))
            
            original_format = original_filename.rsplit('.', 1)[-1]
            audio_bytes = convert_audio_to_wav(audio_bytes, original_format)
            flash(f"Converted {original_format.upper()} to WAV (16-bit PCM) for processing", 'info')
        
        encoded_bytes, metadata = encode_audio(audio_bytes, message, password)
        
        # Save output file
        output_filename = f"stego_{uuid.uuid4()}.wav"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        with open(output_path, 'wb') as f:
            f.write(encoded_bytes)
        
        flash(f"Message encoded successfully! Duration: {metadata['duration']:.2f}s", 'success')
        return render_template('audio.html', 
                               download_file=output_filename,
                               metadata=metadata)
    
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('audio'))
    except Exception as e:
        flash(f'Error encoding audio: {str(e)}', 'error')
        return redirect(url_for('audio'))


@app.route('/audio/decode', methods=['POST'])
def audio_decode():
    """Decode message from audio."""
    if 'audio' not in request.files:
        flash('No audio file provided', 'error')
        return redirect(url_for('audio'))
    
    file = request.files['audio']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('audio'))
    
    password = request.form.get('password') or None
    
    try:
        audio_bytes = file.read()
        message, metadata = decode_audio(audio_bytes, password)
        
        flash('Message decoded successfully!', 'success')
        return render_template('audio.html', 
                               decoded_message=message,
                               decode_metadata=metadata,
                               active_tab='decode')
    
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('audio'))
    except Exception as e:
        flash(f'Error decoding audio: {str(e)}', 'error')
        return redirect(url_for('audio'))


@app.route('/text')
def text():
    """Text steganography page."""
    return render_template('text.html')


@app.route('/text/encode', methods=['POST'])
def text_encode():
    """Encode message into text."""
    cover_text = request.form.get('cover_text', '')
    secret_message = request.form.get('secret_message', '')
    
    if not cover_text:
        flash('Cover text is required', 'error')
        return redirect(url_for('text'))
    
    if not secret_message:
        flash('Secret message is required', 'error')
        return redirect(url_for('text'))
    
    try:
        stego_text = encode_text(cover_text, secret_message)
        
        flash('Message encoded successfully!', 'success')
        return render_template('text.html', 
                               stego_text=stego_text,
                               active_tab='encode')
    
    except Exception as e:
        flash(f'Error encoding text: {str(e)}', 'error')
        return redirect(url_for('text'))


@app.route('/text/decode', methods=['POST'])
def text_decode():
    """Decode message from text."""
    stego_text = request.form.get('stego_text', '')
    
    if not stego_text:
        flash('Stego text is required', 'error')
        return redirect(url_for('text'))
    
    try:
        message = decode_text(stego_text)
        
        flash('Message decoded successfully!', 'success')
        return render_template('text.html', 
                               decoded_message=message,
                               active_tab='decode')
    
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('text'))
    except Exception as e:
        flash(f'Error decoding text: {str(e)}', 'error')
        return redirect(url_for('text'))


@app.route('/analyze')
def analyze():
    """Steganalysis page."""
    return render_template('analyze.html')


@app.route('/analyze/run', methods=['POST'])
def analyze_run():
    """Run steganalysis on uploaded image."""
    if 'image' not in request.files:
        flash('No image file provided', 'error')
        return redirect(url_for('analyze'))
    
    file = request.files['image']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('analyze'))
    
    if not allowed_file(file.filename, 'image'):
        flash('Invalid file type. Please upload PNG, JPG, WebP, or BMP.', 'error')
        return redirect(url_for('analyze'))
    
    try:
        image_bytes = file.read()
        original_filename = file.filename.lower()
        
        # Convert to PNG if needed for analysis
        if not original_filename.endswith(('.png', '.bmp')):
            image_bytes = convert_image_to_png(image_bytes)
            flash(f"Converted {original_filename.rsplit('.', 1)[-1].upper()} to PNG for analysis", 'info')
        
        results = analyze_image(image_bytes)
        
        return render_template('analyze.html', results=results)
    
    except Exception as e:
        flash(f'Error analyzing image: {str(e)}', 'error')
        return redirect(url_for('analyze'))


@app.route('/download/<filename>')
def download(filename):
    """Serve generated output files."""
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        flash('File not found', 'error')
        return redirect(url_for('index'))


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    flash('File too large. Maximum size is 16MB.', 'error')
    return redirect(request.referrer or url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
