from fastapi import requests

from src.configuration.fetch_aws_secrets import fetch_secrets
OPEN_AI_KEY, OPEN_AI_ORG, OPEN_AI_PROJ, ELEVEN_LABS_API_KEY = fetch_secrets()


def convert_text_to_speech(message):


    # define data (Body)
    body ={
        "text": message,
        "voice_settings" :{
            "stability": 0,
            "similarity_boost": 0,
        }
    }


    # Define voice
    voice_rachel = "21m00Tcm4TlvDq8ikWAM"


    # Constructing Headers and Endpoints
    headers = {"xi-api-key": ELEVEN_LABS_API_KEY, "Content-Type": "application/json", "accept" :"audio/mpeg"}
    endpoint = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_rachel}"


    # Send request
    try:
        response = requests.post(endpoint, json=body, headers = headers)
    except Exception as e:
        return

        # Handle Response
    if response.status_code == 200:
        return response.content
    else:
        return