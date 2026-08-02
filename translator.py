import anthropic

client = anthropic.Anthropic()  # 自动读环境变量里的 key

messages = []
print("开始聊天 (Ctrl+C 退出)")

while True:
    user_input = input("\n你: ")
    messages.append({"role": "user", "content": user_input})

    response = client.messages.create(
        # model="claude-sonnet-5",
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system="你是翻译器，把用户输入翻译成德语，只输出译文，不要任何解释",
        temperature=0,
        messages=messages
    )

    reply = next(b.text for b in response.content if b.type == "text")
    messages.append({"role": "assistant", "content": reply})
    print(f"\nClaude: {reply}")



