#!/usr/bin/env python3
"""
Voice Assistant Wrapper for Augment CLI (auggie)
- Speak your message
- It sends to auggie automatically
- Reads the response aloud
"""

import subprocess
import tempfile
import os
import sys
import re

# Global whisper model (loaded once)
WHISPER_MODEL = None

def check_dependencies():
    """Check and install required packages."""
    try:
        import whisper
        import sounddevice
        import numpy
        return True
    except ImportError as e:
        print(f"Missing: {e}")
        print("Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install",
                       "openai-whisper", "sounddevice", "numpy", "-q"])
        return False

def load_whisper():
    """Load whisper model once."""
    global WHISPER_MODEL
    if WHISPER_MODEL is None:
        import whisper
        print("🔄 Loading speech model (one-time)...")
        WHISPER_MODEL = whisper.load_model("base")
    return WHISPER_MODEL

def record_audio(sample_rate=16000):
    """Record audio. Press Ctrl+C to stop."""
    import sounddevice as sd
    import numpy as np

    print("\n🎤 RECORDING... (Ctrl+C to stop)")
    audio_chunks = []

    def callback(indata, frames, time, status):
        audio_chunks.append(indata.copy())

    try:
        with sd.InputStream(samplerate=sample_rate, channels=1, callback=callback):
            while True:
                sd.sleep(100)
    except KeyboardInterrupt:
        pass

    print("⏹️  Stopped.")
    return np.concatenate(audio_chunks, axis=0).flatten() if audio_chunks else None

def transcribe(audio, sample_rate=16000):
    """Transcribe audio using Whisper."""
    import numpy as np
    import wave

    model = load_whisper()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        temp_path = f.name
        with wave.open(temp_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes((audio * 32767).astype(np.int16).tobytes())

    result = model.transcribe(temp_path, language="en")
    os.unlink(temp_path)
    return result["text"].strip()

def clean_for_speech(text):
    """Clean text for text-to-speech."""
    text = re.sub(r'```[\s\S]*?```', ' code block omitted ', text)
    text = re.sub(r'[#*`_\[\]]', '', text)
    text = re.sub(r'https?://\S+', ' link ', text)
    text = re.sub(r'\n+', '. ', text)
    return text.strip()

def split_into_chunks(text, max_sentences=2):
    """Split text into digestible chunks."""
    # Split by sentence endings
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = []

    for s in sentences:
        current.append(s)
        if len(current) >= max_sentences:
            chunks.append(' '.join(current))
            current = []

    if current:
        chunks.append(' '.join(current))

    return chunks

def speak(text, rate=180):
    """Speak text using macOS say."""
    subprocess.run(["say", "-r", str(rate), text])

def speak_interactive(text, rate=180):
    """Speak text in chunks, pausing for user to continue."""
    chunks = split_into_chunks(text)
    total = len(chunks)

    for i, chunk in enumerate(chunks):
        # Speak this chunk
        speak(chunk, rate)

        # If more chunks remain, ask to continue
        if i < total - 1:
            try:
                response = input(f"\n[{i+1}/{total}] ENTER=continue, s=skip, r=repeat: ").strip().lower()
                if response == 's':
                    speak("Skipping rest.")
                    break
                elif response == 'r':
                    speak(chunk, rate)
                    # Re-prompt
                    input(f"[{i+1}/{total}] ENTER=continue: ")
            except KeyboardInterrupt:
                speak("Stopped.")
                break

    print("✅ Done reading.")

def call_auggie(instruction, workspace, continue_session=False, session_id=None):
    """Call auggie CLI and get response."""
    print(f"\n🤖 Sending to Auggie...")

    cmd = [
        "npx", "@augmentcode/auggie",
        "-i", instruction,
        "-w", workspace,
        "--print",
        "--quiet"
    ]

    if session_id:
        # Resume specific session
        cmd.extend(["--resume", session_id])
    elif continue_session:
        cmd.append("--continue")

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=workspace)
    return result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr}"

def get_latest_session_id():
    """Get the most recent auggie session ID."""
    try:
        result = subprocess.run(
            ["npx", "@augmentcode/auggie", "session", "list", "--json"],
            capture_output=True, text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            import json
            sessions = json.loads(result.stdout)
            if sessions and len(sessions) > 0:
                return sessions[0].get("id")
    except:
        pass
    return None

def main():
    print("=" * 50)
    print("🎙️  AUGGIE VOICE ASSISTANT")
    print("=" * 50)

    if not check_dependencies():
        print("Restart after install.")
        return

    # Parse args
    workspace = os.getcwd()
    continue_session = False

    for arg in sys.argv[1:]:
        if arg in ['-c', '--continue']:
            continue_session = True
        else:
            workspace = arg

    print(f"\n📁 Workspace: {workspace}")
    if continue_session:
        print("🔄 Continuing previous session")

    print("\nCommands:")
    print("  ENTER = Record voice message")
    print("  t     = Type text message")
    print("  s     = Show session ID")
    print("  q     = Quit")

    # Pre-load whisper
    load_whisper()

    # Track session
    session_id = None
    if continue_session:
        session_id = get_latest_session_id()
        if session_id:
            print(f"📎 Session ID: {session_id[:8]}...")

    speak("Voice assistant ready.")

    while True:
        prompt = "\n[ENTER=voice, t=text, s=session, q=quit]: "
        cmd = input(prompt).strip()

        if cmd.lower() == 'q':
            speak("Goodbye!")
            break

        if cmd.lower() == 's':
            # Show session info
            sid = session_id or get_latest_session_id()
            if sid:
                print(f"📎 Session ID: {sid}")
                print(f"   Use in auggie: auggie -r {sid[:8]}")
            else:
                print("No session yet.")
            continue

        # Check for text input: t=msg, t = msg, t msg, etc.
        cmd_lower = cmd.lower().strip()

        # Handle various text input formats
        if cmd_lower.startswith('t'):
            rest = cmd[1:].strip()  # Everything after 't'

            # Remove leading '=' if present
            if rest.startswith('='):
                rest = rest[1:].strip()

            if rest:
                # Got message: t=hello, t = hello, t hello
                text = rest
            else:
                # Just 't' or 't=' with nothing after - prompt for message
                text = input("📝 Type your message: ").strip()
                if not text:
                    print("Empty message.")
                    continue
        else:
            # Voice input mode
            audio = record_audio()
            if audio is None or len(audio) == 0:
                speak("No audio recorded.")
                continue

            # Transcribe
            print("🔄 Transcribing...")
            text = transcribe(audio)

        if not text:
            speak("Could not understand.")
            continue

        print(f"\n📝 You: \"{text}\"")
        speak(f"Sending: {text[:50]}")

        # Call auggie
        response = call_auggie(text, workspace, continue_session, session_id)

        print(f"\n🤖 Auggie:\n{response}\n")

        # Speak response interactively (in chunks)
        clean = clean_for_speech(response)
        speak_interactive(clean)

        # After first call, always continue same session
        continue_session = True
        if not session_id:
            session_id = get_latest_session_id()

if __name__ == "__main__":
    main()

