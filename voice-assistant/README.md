# Vauggie - Voice Assistant for Auggie CLI

A voice wrapper around the Augment CLI (`auggie`) that lets you:
- 🎤 Speak to auggie using your voice
- 📝 Or type text messages
- 🔊 Hear responses read aloud
- ⏸️ Pause and continue reading in chunks

## Installation

```bash
# Install dependencies
pip3 install openai-whisper sounddevice numpy

# Make vauggie available globally
ln -sf $(pwd)/vauggie ~/bin/vauggie
export PATH="$HOME/bin:$PATH"
```

## Usage

```bash
# Start voice assistant
vauggie

# Continue previous session
vauggie -c
vauggie --continue
```

## Commands

| Command | Action |
|---------|--------|
| ENTER | Record voice message |
| t | Type text (prompts for input) |
| t=hello | Send text directly |
| t hello | Send text directly |
| s | Show session ID |
| q | Quit |

## While Listening to Response

| Key | Action |
|-----|--------|
| ENTER | Continue to next chunk |
| s | Skip rest of response |
| r | Repeat current chunk |

## Requirements

- Python 3.8+
- macOS (uses `say` command for text-to-speech)
- Microphone access
- Node.js (for auggie CLI)
