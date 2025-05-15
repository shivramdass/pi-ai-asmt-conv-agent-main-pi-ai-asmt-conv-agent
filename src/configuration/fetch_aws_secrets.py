import boto3
import json

def fetch_secrets():
    secret_name = "key-pi-ai-asmt-conv-agent-main-pi-ai-asmt-conv-agent"
    region_name = "ap-south-1"

    client = boto3.client("secretsmanager", region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret_dict = json.loads(response["SecretString"])

        OPEN_AI_KEY = secret_dict.get("OPEN_AI_KEY")
        OPEN_AI_ORG = secret_dict.get("OPEN_AI_ORG")
        OPEN_AI_PROJ = secret_dict.get("OPEN_AI_PROJ")
        ELEVEN_LABS_API_KEY = secret_dict.get("ELEVEN_LABS_API_KEY")

        return OPEN_AI_KEY, OPEN_AI_ORG, OPEN_AI_PROJ, ELEVEN_LABS_API_KEY

    except Exception as e:
        print("Error fetching secrets:", e)
        return None, None, None, None




