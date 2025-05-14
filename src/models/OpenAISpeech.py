import openai

#Panacea's
organization='org-19fiZstGAGxZlawpvFYzmUaW',
project='proj_CMkClfcuUDF1cOF29bAXKRmq',
api_key= "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"


openai.organization = organization
openai.api_key = api_key
def convert_speech_to_text(audio_file):
    try:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        message_text = transcript["text"]
        return message_text

    except Exception as e:
        print(e)
        return