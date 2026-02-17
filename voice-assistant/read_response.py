#!/usr/bin/env python3
"""
Read Clipboard Aloud
- Copy my response from chat
- Run this script
- It reads the response aloud using macOS text-to-speech
"""

import subprocess
import sys

def get_clipboard():
    """Get text from clipboard using pbpaste."""
    result = subprocess.run(["pbpaste"], capture_output=True, text=True)
    return result.stdout

def clean_text(text):
    """Clean text for better speech."""
    # Remove code blocks
    import re
    text = re.sub(r'```[\s\S]*?```', ' code block omitted ', text)
    # Remove markdown
    text = re.sub(r'[#*`_\[\]]', '', text)
    # Remove URLs
    text = re.sub(r'https?://\S+', ' link ', text)
    # Remove multiple newlines
    text = re.sub(r'\n+', '. ', text)
    return text.strip()

def speak(text, rate=180):
    """Speak text using macOS say command."""
    subprocess.run(["say", "-r", str(rate), text])

def main():
    print("📋 Reading clipboard content aloud...")
    
    text = get_clipboard()
    
    if not text:
        print("❌ Clipboard is empty!")
        speak("Clipboard is empty")
        return
    
    # Clean and truncate
    clean = clean_text(text)
    
    # Limit length (say can handle a lot but let's be reasonable)
    if len(clean) > 2000:
        clean = clean[:2000] + "... and more."
        print("⚠️  Text truncated (too long)")
    
    print(f"Speaking {len(clean)} characters...")
    print("-" * 40)
    print(clean[:200] + "..." if len(clean) > 200 else clean)
    print("-" * 40)
    
    speak(clean)
    print("✅ Done!")

if __name__ == "__main__":
    main()

