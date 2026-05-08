"""Text steganography using zero-width Unicode characters."""

# Zero-width Unicode characters for encoding
ZERO_WIDTH_SPACE = '\u200b'      # Represents 0
ZERO_WIDTH_NON_JOINER = '\u200c'  # Represents 1


def encode_text(cover_text, secret_message):
    """
    Encode a secret message into cover text using zero-width characters.
    
    Args:
        cover_text: Visible text to hide message in
        secret_message: Message to hide
        
    Returns:
        str: Cover text with hidden zero-width message
    """
    # Convert secret message to binary
    message_bytes = secret_message.encode('utf-8')
    binary_string = ''.join(format(byte, '08b') for byte in message_bytes)
    
    # Convert binary to zero-width characters
    hidden_chars = ''
    for bit in binary_string:
        if bit == '0':
            hidden_chars += ZERO_WIDTH_SPACE
        else:
            hidden_chars += ZERO_WIDTH_NON_JOINER
    
    # Insert hidden characters between words or at the end
    words = cover_text.split(' ')
    
    if len(words) > 1:
        # Distribute hidden characters between words
        chars_per_gap = max(1, len(hidden_chars) // (len(words) - 1))
        result = words[0]
        char_index = 0
        
        for i in range(1, len(words)):
            # Add hidden characters before this word
            end_index = min(char_index + chars_per_gap, len(hidden_chars))
            result += hidden_chars[char_index:end_index]
            result += ' ' + words[i]
            char_index = end_index
        
        # Add any remaining hidden characters at the end
        if char_index < len(hidden_chars):
            result += hidden_chars[char_index:]
    else:
        # If only one word, append hidden characters at the end
        result = cover_text + hidden_chars
    
    return result


def decode_text(stego_text):
    """
    Decode a hidden message from text with zero-width characters.
    
    Args:
        stego_text: Text containing hidden zero-width characters
        
    Returns:
        str: The decoded secret message
    """
    # Extract zero-width characters
    hidden_chars = ''
    for char in stego_text:
        if char == ZERO_WIDTH_SPACE:
            hidden_chars += '0'
        elif char == ZERO_WIDTH_NON_JOINER:
            hidden_chars += '1'
    
    if not hidden_chars:
        raise ValueError("No hidden message found in text")
    
    # Pad to multiple of 8 bits
    padding = (8 - len(hidden_chars) % 8) % 8
    hidden_chars += '0' * padding
    
    # Convert binary to bytes
    message_bytes = bytes(
        int(hidden_chars[i:i+8], 2) 
        for i in range(0, len(hidden_chars), 8)
    )
    
    # Decode to string
    try:
        message = message_bytes.decode('utf-8').rstrip('\x00')
    except UnicodeDecodeError:
        raise ValueError("Failed to decode hidden message")
    
    return message


def clean_text(stego_text):
    """
    Remove all zero-width characters from text.
    
    Args:
        stego_text: Text with hidden characters
        
    Returns:
        str: Clean text without zero-width characters
    """
    return ''.join(char for char in stego_text 
                   if char not in (ZERO_WIDTH_SPACE, ZERO_WIDTH_NON_JOINER))
