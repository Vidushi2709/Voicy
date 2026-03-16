import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import whisper
from openai import OpenAI
from deepgram import DeepgramClient
import tempfile
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import threading

# Load environment variables
load_dotenv()

class VoiceAIAgent:
    def __init__(self):
        """Initialize the Voice AI Agent with Whisper, OpenRouter, and DeepGram"""
        # Initialize Whisper (ASR)
        print("Loading Whisper model...")
        self.whisper_model = whisper.load_model("base")
        
        # Initialize OpenRouter (LLM)
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY not found in .env file")
        self.llm_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.openrouter_api_key,
        )
        
        # Initialize DeepGram (TTS)
        self.deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
        if not self.deepgram_api_key:
            raise ValueError("DEEPGRAM_API_KEY not found in .env file")
        self.deepgram_client = DeepgramClient(api_key=self.deepgram_api_key)
    
        # Initialize conversation history
        self.conversation_history = []

        # Audio recording settings
        self.sample_rate = 44100
        self.channels = 1
    
    def record_and_transcribe(self) -> str:
        """Record audio and transcribe directly from memory — no file saving"""
        print("Press Enter to START recording...")
        input()

        recorded_frames = []
        stop_event = threading.Event()

        def callback(indata, frames, time, status):
            if not stop_event.is_set():
                recorded_frames.append(indata.copy())

        stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype='float32',
            callback=callback
        )

        with stream:
            print(" Recording... Press Enter to STOP.")
            input()
            stop_event.set()

        if not recorded_frames:
            print("No audio recorded.")
            return None

        # Combine chunks into single array
        audio_data = np.concatenate(recorded_frames, axis=0).flatten()

        # Whisper expects float32 numpy array at 16000hz
        # Resample from 44100 to 16000 if needed
        if self.sample_rate != 16000:
            import scipy.signal as signal
            audio_data = signal.resample(audio_data, int(len(audio_data) * 16000 / self.sample_rate))

        print("Transcribing...")
        result = self.whisper_model.transcribe(audio_data, fp16=False)
        text = result["text"].strip()
        print(f"You said: {text}")
        return text
        
    
    def generate_response(self, user_input: str) -> str:
        """Generate LLM response using OpenRouter"""
        print(f"Generating response for: {user_input}")
        
        # Append user input to history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        message = self.llm_client.chat.completions.create(
            model="mistralai/mistral-small-3.2-24b-instruct",
            messages=self.conversation_history
        )
        response = message.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": "You are a voice assistant. Keep all responses concise, short and under 150 words since they will be spoken aloud. Avoid markdown, bullet points, or special characters like ** or * ."})
        print(f"LLM Response: {response}")
        return response
    
    def synthesize_speech(self, text: str, output_path: str = "output.mp3") -> str:
        """Convert text to speech using DeepGram"""
        print("Synthesizing speech...")

        # Deepgram has a 2000 character limit
        if len(text) > 2000:
            text = text[:1997] + "..."

        audio_stream = self.deepgram_client.speak.v1.audio.generate(
            text=text,
            model="aura-asteria-en",
            encoding="mp3"
        )

        with open(output_path, "wb") as f:
            for chunk in audio_stream:
                f.write(chunk)

        if Path(output_path).exists():
            print(f" Speech saved to {output_path}")
        else:
            print(f" File not created at {output_path}")
        return output_path
    
    def play_audio(self, audio_path: str):
        """Play the synthesized audio response"""
        import subprocess
        abs_path = str(Path(audio_path).resolve())
        
        # Check if file actually exists before playing
        if not Path(abs_path).exists():
            print(f"Audio file not found: {abs_path}")
            return
        
        try:
            if sys.platform == "win32":
                os.startfile(abs_path)
            elif sys.platform == "darwin":
                subprocess.call(["afplay", abs_path])
            else:
                subprocess.call(["mpg123", abs_path])
        except Exception as e:
            print(f"Could not auto-play audio: {e}")
            print(f"Please open manually: {abs_path}")

    def run(self):
        print("\n=== Voice AI Agent (Voice Mode) ===\n")

        turn = 0
        while True:
            # Step 1: Record + Transcribe (no file involved)
            user_text = self.record_and_transcribe()
            if not user_text:
                continue

            if user_text.lower() in ["quit", "exit", "stop"]:
                print("Goodbye!")
                break

            # Step 2: Generate response
            response_text = self.generate_response(user_text)

            # Step 3: Synthesize + Play
            output_path = str(Path(f"response_turn_{turn}.mp3").resolve())
            try:
                self.synthesize_speech(response_text, output_path)
                self.play_audio(output_path)
            except Exception as e:
                print(f"TTS Error: {e}")

            turn += 1

def main():
    try:
        # Initialize the agent
        agent = VoiceAIAgent()

        # run
        agent.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()