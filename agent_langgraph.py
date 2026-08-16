import anthropic
from sentence_transformers import SentenceTransformer
import chromadb
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

# ===== 复用你已有的检索工具（一字没改） =====
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
db_client = chromadb.PersistentClient(path="./chroma_db")
collection = db_client.get_collection("it_support_docs")

# ===== 第1步：定义工具（这次用LangGraph的写法，用@tool装饰器） =====
@tool
def calculator(expression: str) -> str:
    """执行加减乘除运算。适用于任何数学计算问题。参数是数学表达式，比如 '15 * 3'。"""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"计算出错: {e}"

@tool
def search_fabric_docs(query: str) -> str:
    """在Microsoft Fabric技术文档里搜索相关内容。适用于任何关于Fabric、Lakehouse、Dataflow、容量限流等技术问题。"""
    query_embedding = model.encode(query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=2)
    chunks = results["documents"][0]
    return "\n\n".join(chunks)

tools = [calculator, search_fabric_docs]

# ===== 第2步：把模型和工具"绑定"在一起 =====
llm = ChatAnthropic(model="claude-sonnet-4-6")
llm_with_tools = llm.bind_tools(tools)

# ===== 第3步：定义"节点"——图上的每个步骤该做什么 =====
def call_model(state):
    """模型思考节点：看历史，决定下一步说什么/要不要调用工具"""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def call_tools(state):
    """工具执行节点：真正执行模型请求的工具"""
    last_message = state["messages"][-1]
    tool_results = []
    for tool_call in last_message.tool_calls:
        print(f"  [agent决定调用工具: {tool_call['name']}, 参数: {tool_call['args']}]")
        if tool_call["name"] == "calculator":
            result = calculator.invoke(tool_call["args"])
        elif tool_call["name"] == "search_fabric_docs":
            result = search_fabric_docs.invoke(tool_call["args"])
        from langchain_core.messages import ToolMessage
        tool_results.append(ToolMessage(content=result, tool_call_id=tool_call["id"]))
    return {"messages": tool_results}

def should_continue(state):
    """判断节点：模型是想用工具，还是已经给出最终答案了"""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "call_tools"
    return END

# ===== 第4步：把节点和判断逻辑，拼成一张"图" =====
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]

graph = StateGraph(AgentState)
graph.add_node("call_model", call_model)
graph.add_node("call_tools", call_tools)
graph.set_entry_point("call_model")
graph.add_conditional_edges("call_model", should_continue, {"call_tools": "call_tools", END: END})
graph.add_edge("call_tools", "call_model")

app = graph.compile()

# ===== 测试 =====
def run_agent(question):
    result = app.invoke({"messages": [HumanMessage(content=question)]})
    return result["messages"][-1].content

if __name__ == "__main__":
    print(run_agent("15乘以23等于多少？"))
    print("\n" + "="*50 + "\n")
    print(run_agent("What happens when I exceed my Fabric capacity?"))