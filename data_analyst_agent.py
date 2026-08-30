import anthropic
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, BaseMessage
from langchain_core.tools import tool
from typing import TypedDict, Annotated
import operator
import pandas as pd
import io
import contextlib

# ===== 数据 =====
df = pd.read_csv("mrr_data.csv")

# ===== 工具 =====
@tool
def execute_python(code: str) -> str:
    """执行Python代码分析数据。变量df已经预加载（MRR数据，列: customer_id, customer_name,
    industry, region, product, mrr, signup_date, status, churn_date）。
    用print()输出你想看到的结果，我会把打印内容返回给你。"""
    output_buffer = io.StringIO()
    local_vars = {"df": df.copy(), "pd": pd}
    try:
        with contextlib.redirect_stdout(output_buffer):
            exec(code, {"pd": pd}, local_vars)
        output = output_buffer.getvalue()
        return output if output else "代码执行成功，但没有print任何内容。"
    except Exception as e:
        return f"执行出错: {type(e).__name__}: {e}"

tools = [execute_python]

# ===== 模型绑定工具 =====
llm = ChatAnthropic(model="claude-sonnet-4-6")
llm_with_tools = llm.bind_tools(tools)

# ===== system prompt =====
SYSTEM_PROMPT = """你是一名资深数据分析师，帮助管理层理解MRR（月度经常性收入）数据。
用户会用自然语言提问，你需要自己写Pandas代码来回答。

注意：数据中可能存在脏数据（缺失值、非数字字符串等），如果代码执行报错，
请仔细阅读报错信息，判断是否是数据质量问题，并在代码里加入适当的清洗逻辑
（比如用 pd.to_numeric(df['mrr'], errors='coerce') 把无法转换的值变成NaN，再决定是否用dropna()跳过）。

最终回答时，除了给出数字，也要给出简短的业务解读。"""

# ===== 图的三个节点 =====
def call_model(state):
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def call_tools(state):
    last_message = state["messages"][-1]
    tool_results = []
    for tool_call in last_message.tool_calls:
        print(f"\n  [agent决定调用工具: {tool_call['name']}]")
        print(f"  --- 代码 ---\n{tool_call['args']['code']}")
        result = execute_python.invoke(tool_call["args"])
        print(f"  --- 执行结果 ---\n{result}\n")
        tool_results.append(ToolMessage(content=result, tool_call_id=tool_call["id"]))
    return {"messages": tool_results}

def should_continue(state):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "call_tools"
    return END

# ===== 搭图 =====
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]

graph = StateGraph(AgentState)
graph.add_node("call_model", call_model)
graph.add_node("call_tools", call_tools)
graph.set_entry_point("call_model")
graph.add_conditional_edges("call_model", should_continue, {"call_tools": "call_tools", END: END})
graph.add_edge("call_tools", "call_model")

app = graph.compile()

# ===== 运行 =====
def run_agent(question):
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=question)
    ]
    result = app.invoke({"messages": messages})
    return result["messages"][-1].content

if __name__ == "__main__":
    print(run_agent("计算所有客户的MRR总和"))