import ollama

# This sends a message to the model you just downloaded
response = ollama.chat(model='llama3', messages=[
  {
    'role': 'user',
    'content': 'Do u remember my previous chats'

  },
])

print("--- AI RESPONSE ---")
print(response['message']['content'])