import anthropic

client = anthropic.Anthropic()  # 自动读环境变量里的 key

messages = []
print("开始聊天 (Ctrl+C 退出)")

while True:
    user_input = input("\n你: ")
    messages.append({"role": "user", "content": user_input})

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        messages=messages
    )

    reply = next(b.text for b in response.content if b.type == "text")
    # messages.append({"role": "assistant", "content": reply})
    print(f"\nClaude: {reply}")