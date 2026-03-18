import os
import asyncio
from dotenv import load_dotenv
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import deepgram, openai, silero
import time 

load_dotenv()

SYSTEM_PROMPT = """You are a voice assistant. Keep all responses concise and under 150 words 
since they will be spoken aloud. Avoid markdown, bullet points, or special characters like **, . , #, @, & , ^, % , * , ( , ) , { , } , [ , ] , < , > , ? , / , \ , | , " , ' , : , ; , - , _ , = , + , ~ , ` ."""

async def entrypoint(ctx: JobContext):
    ts = {}

    # Connect to the LiveKit room, audio only
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Initial chat context with system prompt
    initial_ctx = llm.ChatContext().append(
        role="system",
        text=SYSTEM_PROMPT
    )

    assistant = VoiceAssistant(
        # VAD: detects when user starts/stops speaking (replaces press-Enter)
        vad=silero.VAD.load(),

        # STT: Deepgram transcribes live audio (replaces Whisper)
        stt=deepgram.STT(
            api_key=os.getenv("DEEPGRAM_API_KEY"),
        ),

        # LLM: OpenRouter with conversation history (same as before)
        llm=openai.LLM(
            model="mistralai/mistral-small-3.2-24b-instruct",
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        ),

        # TTS: Deepgram speaks the response (replaces manual MP3 saving)
        tts=deepgram.TTS(
            api_key=os.getenv("DEEPGRAM_API_KEY"),
            model="aura-asteria-en",
        ),
        chat_ctx=initial_ctx,
    )
    
    # ── Timestamp 1: user stops speaking (VAD detects silence) ─────────────────
    def on_user_stopped_speaking():
        ts["vad_end"] = time.time()
        print(f"[T1 - VAD done]        {ts['vad_end']:.3f}")
 
    # ── Timestamp 2: transcript is ready (STT done) ──────────────────────────
    def on_user_speech_committed(*args):
        ts["stt_done"] = time.time()
        if "vad_end" in ts:
            print(f"[T2 - STT done]        {ts['stt_done']:.3f}  |  STT latency: {(ts['stt_done'] - ts['vad_end']):.3f}s")
        else:
            print(f"[T2 - STT done]        {ts['stt_done']:.3f}  |  vad_end not recorded")
            
    # ── Timestamp 3: assistant starts speaking (TTS audio begins) ────────────
    def on_agent_started_speaking():
        ts["tts_start"] = time.time()
        if "stt_done" in ts:
            print(f"[T3 - TTS audio start] {ts['tts_start']:.3f}  |  LLM+TTS latency: {(ts['tts_start'] - ts['stt_done']):.3f}s")
        else:
            print(f"[T3 - TTS audio start] {ts['tts_start']:.3f}  |  stt_done not recorded")
        if "vad_end" in ts:
            print(f"                                        End-to-end latency: {(ts['tts_start'] - ts['vad_end']):.3f}s")
        else:
            print(f"                                        End-to-end latency: vad_end not recorded")
 
    # assistant.on starts an event 
    assistant.on("user_stopped_speaking",  on_user_stopped_speaking)
    assistant.on("user_speech_committed",  on_user_speech_committed)
    assistant.on("agent_started_speaking", on_agent_started_speaking)

    # Start the assistant in the room
    assistant.start(ctx.room)

    # Greet the user
    await asyncio.sleep(1)
    await assistant.say("Hey! I'm your voice assistant. How can I help you today?", allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint
        )
    )
