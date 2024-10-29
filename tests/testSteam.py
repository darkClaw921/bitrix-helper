import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
import asyncio
from dotenv import load_dotenv
load_dotenv()
# Установите ваш API ключ OpenAI
api_key = os.getenv('OPENAI_API_KEY')

asyncClient = AsyncOpenAI(api_key=api_key)
app = FastAPI()

@app.post("/synthesize/")
async def synthesize_voice(text: str):
    try:
        # Запрос к OpenAI для синтеза речи
        response = AsyncOpenAI.audio.speech.with_streaming_response.create(
            model="text-to-speech",
            input=text,
            response_format="streaming"
        )

        async def generate_audio():
            for chunk in response:
                if 'audio_content' in chunk:
                    yield chunk['audio_content']

        return StreamingResponse(generate_audio(), media_type="audio/mpeg")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)