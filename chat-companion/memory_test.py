from sentence_transformers import SentenceTransformer
import chromadb
import anthropic
client = anthropic.Anthropic()
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
db_client = chromadb.PersistentClient(path="./chroma_db")
collection = db_client.get_or_create_collection("chat_memory")

import time
from datetime import datetime

def save_memory(user_msg, ai_reply):
    combined_text = f"user said: {user_msg}\nAI replied: {ai_reply}"

    embedding = model.encode(combined_text).tolist()

    unique_id = str(time.time())
    timestamp = datetime.now().isoformat()

    collection.add(
        ids=[unique_id],
        embeddings=[embedding],
        documents=[combined_text],
        metadatas=[{"timestamp": timestamp, "topic": "unclassified"}]
    )



def chat_with_memory(user_input):
    # Step 1: check for relevant past memory
    memory_result = search_memory(user_input)

    # Step 2: build the content to send Claude, depending on whether memory was found
    if memory_result is not None:
        retrieved_chunks = memory_result["documents"][0]
        context = "\n\n".join(retrieved_chunks)
        content_to_send = f"Here is some relevant past conversation:\n{context}\n\nThe user now says: {user_input}"
    else:
        content_to_send = user_input

    # Step 3: call Claude and get the reply
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system="You are the user's warm, close friend. Speak naturally, like an old friend catching up.",
        messages=[{"role": "user", "content": content_to_send}]
    )
    reply = next(b.text for b in response.content if b.type == "text")

    # Step 4: save this turn into long-term memory
    save_memory(user_input, reply)

    return reply


def search_memory(current_msg):
    keywords = ["before", "last time", "remember"]
    if any(word in current_msg.lower() for word in keywords):
        encoding = model.encode(current_msg).tolist()
        results = collection.query(query_embeddings=[encoding], n_results=2)
        return results
    else:
        return None


if __name__ == "__main__":
    print("Chat started (Ctrl+C to exit)")
    while True:
        user_input = input("\nYou: ")
        reply = chat_with_memory(user_input)
        print(f"\nAI: {reply}")