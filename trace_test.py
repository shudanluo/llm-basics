from dotenv import load_dotenv
load_dotenv()

from langfuse import observe, get_client

client = get_client()
print("auth ok:", client.auth_check())

@observe()
def shout(text):
    return text.upper()

print(shout("hello"))
client.flush()

from rag_test import ask

@observe()
def traced_ask(question):
    return ask(question)

print(traced_ask("What does Dataflow Gen2 use as its underlying engine?"))
client.flush()