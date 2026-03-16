# 🎙️ Voicy

Voicy is a real-time Voice AI Agent that allows for seamless voice-to-voice interaction. It comes in two flavours — a lightweight local version and a production-ready LiveKit-powered version.

---

## 🚀 Features

- **ASR (Automatic Speech Recognition):** Powered by OpenAI's **Whisper** (local) or **Deepgram STT** (LiveKit mode) for accurate, multi-lingual transcription.
- **Intelligence:** Integrated with **OpenRouter**, utilizing advanced models (e.g., Mistral) for smart and concise reasoning.
- **TTS (Text-to-Speech):** Utilizes **Deepgram's Aura** for fast, human-like voice responses.
- **Two Modes:** Run locally with a simple CLI, or deploy as a real-time agent with LiveKit.

---

## 🗂️ Project Structure

```
voicy/
├── voicy.py           # Local CLI version (no server needed)
├── livekit_voicy.py   # LiveKit version (real-time, browser-accessible)
├── .env               # Your API keys
└── requirements.txt
```

---

## 🛠️ Prerequisites

- **Python 3.11+**
- **API Keys:**
  - [OpenRouter API Key](https://openrouter.ai/)
  - [Deepgram API Key](https://console.deepgram.com/)
  - [LiveKit Cloud Account](https://cloud.livekit.io/) *(only for livekit_voicy.py)*

---

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Vidushi2709/Voicy.git
   cd voicy
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   # or
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory:
   ```env
   # Required for both versions
   OPENROUTER_API_KEY=your_openrouter_key_here
   DEEPGRAM_API_KEY=your_deepgram_key_here

   # Required only for livekit_voicy.py
   LIVEKIT_API_KEY=your_livekit_api_key
   LIVEKIT_API_SECRET=your_livekit_api_secret
   LIVEKIT_URL=wss://your-project.livekit.cloud
   ```

---

## 🎮 Usage

### Option 1 — `voicy.py` (Local CLI)

No server needed. Runs entirely on your machine.

```bash
python voicy.py
```

**How it works:**
1. Press `Enter` to start recording.
2. Speak your message.
3. Press `Enter` again to stop.
4. The agent transcribes, thinks, and speaks back.
5. Say `quit`, `exit`, or `stop` to end the session.

**Pipeline:**
```
Mic (sounddevice) → Whisper (local STT) → OpenRouter LLM → Deepgram TTS → Speaker
```

---

### Option 2 — `livekit_voicy.py` (LiveKit Real-Time Agent)

Runs as a live agent accessible from any browser. Requires a LiveKit Cloud account.

```bash
python livekit_voicy.py dev
```

Then open the LiveKit playground to talk to your agent:
```bash
start https://agents-playground.livekit.io   # Windows
open https://agents-playground.livekit.io    # Mac
```

Connect using your LiveKit Cloud credentials and start talking — no Enter key needed.

**Pipeline:**
```
Browser Mic → Deepgram STT (streaming) → OpenRouter LLM → Deepgram TTS → Browser Speaker
```

---

## ⚖️ voicy.py vs livekit_voicy.py

| | `voicy.py` | `livekit_voicy.py` |
|---|---|---|
| **Lines of code** | ~150 | ~50 |
| **Setup** | Just API keys | API keys + LiveKit Cloud |
| **STT** | Whisper (runs locally) | Deepgram (streaming) |
| **Turn detection** | Press Enter | Auto VAD (detects silence) |
| **Latency** | Medium (local processing) | Low (real-time streaming) |
| **Works over internet** | No (local only) | Yes |
| **Multi-user** | No | Yes (rooms) |
| **Best for** | Local use, learning, no infra | Production, demos, real users |

The LiveKit version reduces ~100 lines of manual audio/recording/playback code down to a single `VoiceAssistant` object — LiveKit handles the entire pipeline automatically.

---

## 🏗️ How It Works

### `voicy.py` (Manual Pipeline)
1. **Recording:** Captures mic audio using `sounddevice` as a float32 array in memory.
2. **Transcription:** Resamples to 16kHz and feeds directly into Whisper — no file saved to disk.
3. **LLM:** Text sent to OpenRouter with full conversation history for context.
4. **Synthesis:** Response sent to Deepgram, audio streamed back as MP3 chunks and saved locally.
5. **Playback:** MP3 opened via the system's default media player.

### `livekit_voicy.py` (LiveKit Pipeline)
1. **VAD:** Silero VAD detects when you start and stop speaking automatically.
2. **STT:** Deepgram transcribes your audio in real-time as you speak.
3. **LLM:** OpenRouter generates a response with conversation memory.
4. **TTS:** Deepgram streams audio back directly to your browser — no files involved.

---

## 📝 License

This project is open-source and available under the MIT License.

---

## Contribution?

You like it? You can have it :)