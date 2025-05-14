from openai import OpenAI
client = OpenAI(
  organization='org-QfkXSYTTOVxDVKO30ZxwXfAv',
  project='proj_jhBGXwroVW3oWnlsoFcr1G1Z',
  api_key= "sk-Pct3_cnOKaMvyvy5ZCwU0X-jDqEMj9spg5rIezADNGT3BlbkFJLTCTcn3oEK-Qn0GnoHnWmt_hUHItB7DanbbIkLp2MA"
)


system_prompt ='''You are an experienced PCI DSS auditor. Given the following ###question, and possible ###responses_choices, as the overarching context, evaluate the response of the user to find out which reponse the user's comment maps to. The user's comment may also map to some additional ###Actions. 
  Always give your decision/response in the following format 'The user's response maps to: <mapped choice>'.-

###question: What type of merchant you are?

###responses_choices -

Online
Brick and Mortar
Hybrid

###Actions

Asking Clarifying question
Irrelevant to the question
Asking to go back
Asking to save and exit
Asking to skip to next question
Asking to restart the assessment

Also, please take care of some general guidelines while you process user's response -

If you cannot decide which ###responses_choices or ###Actions the user's comment maps to, then respond with 'The user's response maps to: Cant't Decide'
If merchant accepts payment through QR code provided by payment gateway, it is an "online" merchant

'''

stream = client.chat.completions.create(
  # model="gpt-4",
  model = "gpt-4o-mini",
  messages=[
    {
      "role": "system",
      "content": system_prompt
    },
    {
      "role": "user",
      "content": "To sell my products and services i take payment through my website"
      # "content": "Tell me a joke"
    }
  ],
  temperature=0.7,
  max_tokens=64,
  top_p=1,
  # stream = True
)

resp = ""
# for chunk in stream:
#     if chunk.choices[0].delta.content is not None:
#         print(chunk.choices[0].delta.content, end="")

for choice in stream.choices:
  resp = resp + " " + choice.message.content

print(resp)