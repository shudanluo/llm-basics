import anthropic
from sentence_transformers import SentenceTransformer
import chromadb

client = anthropic.Anthropic()
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
db_client = chromadb.PersistentClient(path="./chroma_db")
collection = db_client.get_collection("it_support_docs")

# ===== 第1步：定义"工具箱"里有什么，告诉模型 =====
tools = [
    {
        "name": "calculator",
        "description": "执行加减乘除运算。适用于任何数学计算问题。",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "数学表达式，比如 '15 * 3' 或 '100 / 4'"}
            },
            "required": ["expression"]
        }
    },
    {
        "name": "search_fabric_docs",
        "description": "在Microsoft Fabric技术文档里搜索相关内容。适用于任何关于Fabric、Lakehouse、Dataflow、容量限流等技术问题。",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "要搜索的问题或关键词"}
            },
            "required": ["query"]
        }
    }
]

# ===== 第2步：真正的工具执行函数（模型只会"请求"调用，这里才是真的执行） =====
def calculator(expression):
    try:
        result = eval(expression)  # 简化写法，生产环境不要用eval，这里学习用
        return str(result)
    except Exception as e:
        return f"计算出错: {e}"

def search_fabric_docs(query):
    query_embedding = model.encode(query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=2)
    chunks = results["documents"][0]
    return "\n\n".join(chunks)

# ===== 第3步：agent主循环 =====
def run_agent(user_question):
    messages = [{"role": "user", "content": user_question}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )

        # 把模型这一轮的完整回复存进历史（可能包含文字+工具调用请求）
        messages.append({"role": "assistant", "content": response.content})

        # 检查模型是不是想结束对话了（给出最终答案）
        if response.stop_reason != "tool_use":
            # 模型没有请求用工具，说明它给出了最终答案
            final_text = next((b.text for b in response.content if b.type == "text"), "")
            return final_text

        # 模型请求用工具——找出是哪个工具、什么参数
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                tool_name = block.name
                tool_input = block.input
                print(f"  [agent决定调用工具: {tool_name}, 参数: {tool_input}]")

                # 真正执行对应的Python函数
                if tool_name == "calculator":
                    result = calculator(tool_input["expression"])
                elif tool_name == "search_fabric_docs":
                    result = search_fabric_docs(tool_input["query"])
                else:
                    result = "未知工具"

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        # 把工具执行结果塞回历史，继续下一轮循环
        messages.append({"role": "user", "content": tool_results})


# ===== 测试 =====
if __name__ == "__main__":
    print(run_agent("15乘以23等于多少？"))
    print("\n" + "="*50 + "\n")
    print(run_agent("What is the key difference between skill and agent?"))
