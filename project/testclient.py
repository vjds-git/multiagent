from project_starter import client, MODEL

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "user", "content": "Say hello in one sentence."}
    ]
)

print("Model response:", response.choices[0].message.content)
print("Client working!")
