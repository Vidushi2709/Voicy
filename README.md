# 🎙️ Voicy

Voicy is a real-time Voice AI Agent that allows for seamless voice-to-voice interaction. 

## 🚀 Features

- **ASR (Automatic Speech Recognition):** Powered by OpenAI's **Whisper** for accurate, multi-lingual transcription.
- **Intelligence:** Integrated with **OpenRouter**, utilizing advanced models (e.g., Mistral) for smart and concise reasoning.
- **TTS (Text-to-Speech):** Utilizes **Deepgram's Aura** for fast, human-like voice responses.
- **Minimal Latency:** Optimized audio handling with direct memory processing to minimize turnaround time.
- **Simple Interface:** Easy-to-use CLI—just press Enter to talk.

## 🛠️ Prerequisites

- **Python 3.11+**
- **API Keys:**
  - [OpenRouter API Key](https://openrouter.ai/)
  - [Deepgram API Key](https://console.deepgram.com/)
- **System Dependencies:**
  - For Windows: Audio drivers usually suffice.
  - For Linux: You may need `mpg123` for audio playback.

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Vidushi2709/Voicy.git
   cd voicy
   ```

2. **Install dependencies:**
   This project uses `uv` for lightning-fast dependency management:
   ```bash
   uv sync
   ```
   *Alternatively, using pip:*
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory and add your keys:
   ```env
   OPENROUTER_API_KEY=your_openrouter_key_here
   DEEPGRAM_API_KEY=your_deepgram_key_here
   ```

## 🎮 Usage

Run the agent with:
```bash
python main.py
```

### How to use:
1. **Start Recording:** Press `Enter` and start speaking.
2. **Stop Recording:** Press `Enter` again when finished.
3. **Listen:** The agent will transcribe your voice, generate a response, and speak it back to you.
4. **Exit:** Type `quit`, `exit`, or `stop` during the prompt to end the session.

## 🏗️ How it Works

1. **Recording:** Captures audio using `sounddevice` as a float32 array.
2. **Transcription:** Resamples the audio to 16kHz and feeds it into the **Whisper** `base` model.
3. **LLM Loop:** Transmitted text is sent to **OpenRouter**. The system is prompted to keep responses short and concise for optimal voice delivery.
4. **Synthesis:** The response text is sent to **Deepgram** to generate an MP3 audio stream.
5. **Playback:** The generated MP3 is saved locally and played using the system's default media player.

## 📝 License

This project is open-source and available under the MIT License.

## Contribution?

you like it? you can have it :) 