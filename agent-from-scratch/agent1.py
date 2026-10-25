import anthropic

client = anthropic.Anthropic()

messages = []

while True:
    user_input = input("You:")
    if user_input == "quit":
        break

    messages.append({"role":"user", "content":user_input})

    response = client.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=1024,
            messages=messages                                                       # NEW
        )
    reply = next(b.text for b in response.content if b.type == "text")
    print(reply)
    messages.append({"role":"assistant", "content":reply})