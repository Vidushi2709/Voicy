import os
import asyncio
from dotenv import load_dotenv
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import deepgram, openai, silero

load_dotenv()

SYSTEM_PROMPT = """You are a voice assistant. Keep all responses concise and under 150 words 
since they will be spoken aloud. Avoid markdown, bullet points, or special characters like **, . , #, @, & , ^, % , * , ( , ) , { , } , [ , ] , < , > , ? , / , \ , | , " , ' , : , ; , - , _ , = , + , ~ , ` ."""


async def entrypoint(ctx: JobContext):
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
            http_session=None,  # force fresh session
        ),

        # LLM: OpenRouter with conversation history (same as before)
        llm=openai.LLM(
            model="mistralai/mistral-small-3.2-24b-instruct",
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            http_session=None,  # force fresh session
        ),

        # TTS: Deepgram speaks the response (replaces manual MP3 saving)
        tts=deepgram.TTS(
            api_key=os.getenv("DEEPGRAM_API_KEY"),
            model="aura-asteria-en",
            http_session=None,  # force fresh session
        ),

        chat_ctx=initial_ctx,
    )

    # Start the assistant in the room
    assistant.start(ctx.room)

    # Greet the user
    await asyncio.sleep(1)
    await assistant.say("Hey! I'm your voice assistant. How can I help you today?", allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            api_key=os.getenv("LIVEKIT_API_KEY"),
            api_secret=os.getenv("LIVEKIT_API_SECRET"),
            ws_url=os.getenv("LIVEKIT_URL"),
        )
    )