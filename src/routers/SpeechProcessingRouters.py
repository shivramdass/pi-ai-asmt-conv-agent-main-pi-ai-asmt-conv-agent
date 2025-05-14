from fastapi import APIRouter
from fastapi import Response, Request
from fastapi.responses import StreamingResponse
from io import BytesIO
from pydub import AudioSegment

from src.models.ElevenLabs import convert_text_to_speech
from src.models.OpenAISpeech import convert_speech_to_text
from fastapi import HTTPException

router = APIRouter()


@router.post("/text-to-speech")
async def text_to_speech(request: Request):
    # Extract JSON data from the request body
    data = await request.json()
    text = data['text']  # Access the text field directly

    audio_output = convert_text_to_speech(text)

    # Create a generator that yields chunks of data
    def iterfile():
        yield audio_output

        # Return audio file

    return StreamingResponse(iterfile(), media_type="application/octet-stream")


@router.post("/speech-to-text/")
async def speech_to_text(request: Request):
    try:
        # Read the raw bytes from the request body
        file_bytes = await request.body()

        # Use BytesIO to create an in-memory file from the bytes
        audio_file = BytesIO(file_bytes)

        # Load the audio from the in-memory file (assumes it's in a supported format, like WAV)
        audio = AudioSegment.from_file(audio_file)

        # Convert the audio to MP3 format in-memory
        converted_audio = BytesIO()
        audio.export(converted_audio, format="mp3")  # Convert to MP3
        converted_audio.seek(0)  # Rewind the BytesIO object to the beginning

        # Decode the audio to text using your custom function
        message_decoded = convert_speech_to_text(converted_audio)

        # Guard: Ensure the message is decoded
        if not message_decoded:
            raise HTTPException(status_code=400, detail="Failed to decode audio")

            # Return the chat response as plain text
        return Response(content=message_decoded, media_type="text/plain")


    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid audio file format: {str(e)}")