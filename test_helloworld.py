from openai import OpenAI

client = OpenAI(
  organization='org-QfkXSYTTOVxDVKO30ZxwXfAv',
  project='proj_jhBGXwroVW3oWnlsoFcr1G1Z',
  api_key= "sk-Pct3_cnOKaMvyvy5ZCwU0X-jDqEMj9spg5rIezADNGT3BlbkFJLTCTcn3oEK-Qn0GnoHnWmt_hUHItB7DanbbIkLp2MA"
)

from openai import OpenAI

# client = OpenAI("sk-Pct3_cnOKaMvyvy5ZCwU0X-jDqEMj9spg5rIezADNGT3BlbkFJLTCTcn3oEK-Qn0GnoHnWmt_hUHItB7DanbbIkLp2MA")

stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say this is a test"}],
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")




# [
#       {
#         "role": "user",
#         "content": "can you explain mpore about the question that you asking?",
#         "intent": "clarifying question"
#       },
#       {
#         "role": "assistant",
#         "content": "answer ansewe b;ah blah"
#       },
#     {
#         "role": "user",
#         "content": "tell me a joke?",
#         "intent": "irrelevant"
#     },
#     {
#        "role": "assistant",
#        "content": "Answer, and then reiterate that user must confine himself to the task at hand"
#
#     },
#
#     ]