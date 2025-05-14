from openai import OpenAI
import os
from dotenv import load_dotenv
import ollama
import re
from src.routers.model import AsmtChatResponse, AsmtChatResponseSingle
from src.models.asmt_prompts import (
    intent_system_prompt,
    multiple_response_choices_prompt,
    short_answer_prompt,
    long_answer_prompt,
    clarification_system_prompt,
    irrelevant_system_prompt
)

load_dotenv()
OPENAI_KEY = os.getenv('OPEN_AI_KEY')
OPENAI_ORG = os.getenv('OPEN_AI_ORG')
OPENAI_PROJ = os.getenv('OPENAI_PROJ')

client = OpenAI(organization=OPENAI_ORG, project=OPENAI_PROJ, api_key=OPENAI_KEY)

OLLAMA_MODELS = ["gemma3:4b", "phi4-mini:3.8b", "qwen2.5:3b", "mistral:7b-instruct", "deepseek-r1:1.5b", "deepseek-llm:7b"]

def format_message_prompt(question, question_explaination, response_choices, responsetype, additional_knowledge, user_comment):
    prompt_mapping = {
        "radio": intent_system_prompt,
        "checkbox": multiple_response_choices_prompt,
        "short_answer": short_answer_prompt,
        "long_answer": long_answer_prompt
    }
    formatted_content = prompt_mapping.get(responsetype).format(
        question, question_explaination, "\n".join(response_choices), additional_knowledge,
    )
    return [
        {"role": "system", "content": formatted_content},
        {"role": "user", "content": user_comment}
    ]

def process_chat_history(chat_history):
    chat_history_dicts = [chat.dict() for chat in chat_history]
    last_irrelevant_index = -1
    i = 0
    
    while i < len(chat_history_dicts):
        if chat_history_dicts[i].get('intent') == 'Irrelevant to the question':
            if last_irrelevant_index == i:
                return chat_history_dicts, True
            del chat_history_dicts[i]
            last_irrelevant_index = i
            if i < len(chat_history_dicts):
                del chat_history_dicts[i]
        else:
            i += 1

    for d in chat_history_dicts:
        d.pop('intent', None)
        
    return chat_history_dicts, False

def clean_text(text):
    replacements = {
        "–": "-",
        "—": "-",
        "’": "'",
        "“": "'",
        "”": "'",
        "#": "",
        "\n": "",
        "_": " ",
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    return text

def generate_response(messages):
   # First try OpenAI GPT-4
    try:
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=80,
            top_p=1
        )
        return " ".join(choice.message.content for choice in stream.choices)
    except Exception as e:
        print(f"OpenAI request failed: {e}. Trying Ollama models...")

    # Fallback to Ollama models in specified order
    for model_name in OLLAMA_MODELS:
        try:
            response = ollama.chat(
                model=model_name,
                messages=messages,
                options={
                    'temperature': 0.1,
                    'num_predict': 1000,
                    'top_p': 1
                }
            )
            response_message = response['message']['content']
            response_message = clean_text(response_message)
            final_answer = re.sub(r"<think>.*?</think>", "", response_message, flags=re.DOTALL).strip()
            return final_answer
        except Exception as ollama_e:
            print(f"Model {model_name} failed: {ollama_e}")
            continue

    raise Exception("All models failed to generate a response.")
    
def get_intent_response(question, question_explaination, response_choices, responsetype, user_comment, additional_knowledge, chat_history):
    if responsetype not in ["radio", "checkbox", "short_answer", "long_answer"]:
        raise ValueError("Invalid question type")

    message_prompt = format_message_prompt(question, question_explaination, response_choices, responsetype, additional_knowledge, user_comment)
    chat_history_dicts, consecutive_irrelevant_found = process_chat_history(chat_history)

    chat_history_dicts.extend(message_prompt)

    if consecutive_irrelevant_found:
        return AsmtChatResponse(response=[
            AsmtChatResponseSingle(role="user", content=user_comment, intent="Good Response"),
            AsmtChatResponseSingle(role="assistant", content="STOP", intent="STOP")
        ])

    response_text = generate_response(chat_history_dicts)
    result = response_text.split("The user's response maps to: ", 1)[-1].strip()

    return process_response(result, question, question_explaination, response_choices, responsetype, user_comment, additional_knowledge, chat_history)

def process_response(result, question, question_explaination, response_choices, responsetype, user_comment, additional_knowledge, chat_history):
    if responsetype == "checkbox":
      if "Asking Clarifying question" in result:
        return get_clarification(question, question_explaination, response_choices, responsetype, user_comment, additional_knowledge, chat_history)
      elif "Irrelevant to the question" in result:
         return get_irrelevant_response(question, question_explaination, response_choices, responsetype, user_comment, additional_knowledge, chat_history)
      else:
        mapped_choices = result.split(", ")  # The result contains a comma-separated list of choices mapped by the model
        return AsmtChatResponse(response=[
          AsmtChatResponseSingle(role="user", content=user_comment, intent="Good Response"),
          AsmtChatResponseSingle(role="assistant", content=", ".join(mapped_choices), intent="Select and proceed")
      ])
        
    elif responsetype == "radio":
        if any(choice in result for choice in response_choices):
            return AsmtChatResponse(response=[
                AsmtChatResponseSingle(role="user", content=user_comment, intent="Good Response"),
                AsmtChatResponseSingle(role="assistant", content=result, intent="Select and proceed")
            ])
        elif "Asking Clarifying question" in result:
            return get_clarification(question, question_explaination, response_choices, responsetype, user_comment, additional_knowledge, chat_history)
        elif "Irrelevant to the question" in result:
            return get_irrelevant_response(question, question_explaination, response_choices, responsetype, user_comment, additional_knowledge, chat_history)
    
    elif responsetype == "long_answer":
      if "Asking Clarifying question" in result:
        return get_clarification(question, question_explaination, response_choices, responsetype, user_comment, additional_knowledge, chat_history)
      elif "Irrelevant to the question" in result:
         return get_irrelevant_response(question, question_explaination, response_choices, responsetype, user_comment, additional_knowledge, chat_history)
      else:
        return AsmtChatResponse(response=[
          AsmtChatResponseSingle(role="user", content=user_comment, intent="Good Response"),
          AsmtChatResponseSingle(role="assistant", content=result, intent="Select and proceed")
      ])

    elif responsetype == "short_answer":
      if "Asking Clarifying question" in result:
        return get_clarification(question, question_explaination, response_choices, responsetype, user_comment, additional_knowledge, chat_history)
      elif "Irrelevant to the question" in result:
         return get_irrelevant_response(question, question_explaination, response_choices, responsetype, user_comment, additional_knowledge, chat_history)
      else:
        return AsmtChatResponse(response=[
          AsmtChatResponseSingle(role="user", content=user_comment, intent="Good Response"),
          AsmtChatResponseSingle(role="assistant", content=result, intent="Select and proceed")
      ])

    return AsmtChatResponse(response=[
        AsmtChatResponseSingle(role="user", content=user_comment, intent="ACTION"),
        AsmtChatResponseSingle(role="assistant", content=result, intent="ACTION")
    ])


def get_clarification(question, question_explaination, response_choices, responsetype, user_comment, additional_knowledge, chat_history):
    message_prompt = [
        {"role": "system", "content": clarification_system_prompt.format(question, question_explaination, response_choices, additional_knowledge)},
        {"role": "user", "content": user_comment}
    ]
    return handle_response(message_prompt, chat_history, user_comment, "Clarifying Question", "Speak the response")

def get_irrelevant_response(question, question_explaination, response_choices, responsetype, user_comment, additional_knowledge, chat_history):
    message_prompt = [
        {"role": "system", "content": irrelevant_system_prompt.format(question, question_explaination, response_choices)},
        {"role": "user", "content": user_comment}
    ]
    return handle_response(message_prompt, chat_history, user_comment, "Irrelevant to the question", "Speak the response")

def handle_response(message_prompt, chat_history, user_comment, user_intent, assistant_intent):
    chat_history_dicts, consecutive_irrelevant_found = process_chat_history(chat_history)
    chat_history_dicts.extend(message_prompt)

    if consecutive_irrelevant_found:
        return AsmtChatResponse(response=[
            AsmtChatResponseSingle(role="user", content=user_comment, intent=user_intent),
            AsmtChatResponseSingle(role="assistant", content="STOP", intent="STOP")
        ])

    response_text = generate_response(chat_history_dicts)
    response_text = clean_text(response_text)
    result = response_text.split("Answer to the user's request is: ", 1)[-1].strip()
    result = result.split("Answer to the user's question is: ", 1)[-1].strip()

    return AsmtChatResponse(response=[
        AsmtChatResponseSingle(role="user", content=user_comment, intent=user_intent),
        AsmtChatResponseSingle(role="assistant", content=result, intent=assistant_intent)
    ])
