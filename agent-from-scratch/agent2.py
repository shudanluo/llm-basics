import anthropic
from datetime import datetime

client = anthropic.Anthropic()

# NEW 1: describe the tool to Claude
tools = [
    {
        "name": "get_time",
        "description": "Returns the current date and time. Use it when the user asks what time or date it is.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "word_count",
        "description": "Counts the number of words in a given text. Use it when the user asks how many words a text contains",     # you write this: what it does and when to use it
        "input_schema": {
            "type": "object",
            "properties": {"text": {"type": "string", "description": "The text whose words should be counted"}},
            "required": ["text"],
        },
    },
]



def word_count(text):
    return len(text.split())

    
# NEW 2: the real function
def get_time():
    return datetime.now().isoformat()

MAX_STEPS = 5   

messages = []

while True:
    user_input = input("You:")
    if user_input == "quit":
        break

    messages.append({"role":"user", "content":user_input})

    # NEW 3: an inner loop, because Claude may ask for tools several times

    for step in range(MAX_STEPS): 
        response = client.messages.create(
                model="claude-sonnet-5-5",
                max_tokens=1024,
                tools = tools,
                messages=messages,                                                       # NEW
            )
        messages.append({"role":"assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            break

        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                try:
                    if block.name == "get_time":
                        result = get_time()
                    elif block.name == "word_count":
                        result = str(word_count(block.input["text"]))

                    else:
                        result = "unknown tool"
                        
                    
                    
                except Exception as e:
                    result = f"Tool error : {type(e).__name__}:{e}"
                
                tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

        messages.append({"role":"user", "content":tool_results})
        print("DEBUG:", response.stop_reason, [b.type for b in response.content])
    else:                                   # same column as the "for step" line
        print("Stopped: reached the maximum number of steps.")
        continue

    reply = next(b.text for b in response.content if b.type == "text")
    print(reply)

                    
