import anthropic
import json
import pandas as pd

client = anthropic.Anthropic()

df = pd.read_csv("customer_feedback.csv")

sentiments, topics, urgencies = [], [], []

for i, row in df.iterrows():
    fb = row["feedback"]
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            temperature=0,
            system="""你是客户反馈分类器。只输出合法JSON，不要markdown代码块，不要任何解释。
    格式: {"sentiment": "positive/neutral/negative", "topic": "bug/feature_request/praise/billing/other", "urgency": "high/medium/low"}

    示例:
    输入: 系统又崩了，第三次了！
    输出: {"sentiment": "negative", "topic": "bug", "urgency": "high"}

    输入: 能不能加个导出Excel的功能
    输出: {"sentiment": "neutral", "topic": "feature_request", "urgency": "low"}"""
    ,
            messages=[{"role": "user", "content": fb}]
        )
        reply = next(b.text for b in response.content if b.type == "text")

        reply = reply.replace("```json", "").replace("```", "").strip()
        result = json.loads(reply)
        print(f"{fb} → {result['sentiment']} | {result['topic']} | {result['urgency']}")
        sentiments.append(result['sentiment'])
        topics.append(result['topic'])
        urgencies.append(result['urgency'])
    except Exception as e:
        sentiments.append("error")
        topics.append("error")
        urgencies.append("error")
        print(f"{fb} → ERROR: {e}")

df["sentiment"] = sentiments
df["topic"] = topics
df["urgency"] = urgencies
df.to_csv("classified_feedback.csv", index=False)
print(df["sentiment"].value_counts())

# ===== 分析师层：第 1 步，拼材料 =====

stats = df["sentiment"].value_counts().to_string()

critical = df[(df["sentiment"] == "negative") & (df["urgency"] == "high")]

material = f"情感分布:\n{stats}\n\n最严重的反馈:\n"
for i, row in critical.iterrows():
    material += f"- {row['customer']}: {row['feedback']}\n"

print("\n========== 给分析师的材料 ==========")
print(material)

# ===== 分析师层：第 2 步，调用 LLM =====

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=2048,
    temperature=0,
    system="""你是一家德国MSP公司(微软云服务商)的客户体验分析师。
基于用户提供的反馈数据，输出分析英语报告。
只输出合法JSON，不要markdown代码块，不要任何解释。格式:
{
  "summary": "2-3句话的整体状况评估",
  "top_issues": ["最突出的3个问题主题"],
  "anomalies": ["需要管理层立刻关注的异常情况，带客户名"],
  "recommended_actions": ["2-3条具体可执行的建议"]
}""",
    messages=[{"role": "user", "content": material}]
)

reply = next(b.text for b in response.content if b.type == "text")
reply = reply.replace("```json", "").replace("```", "").strip()
report = json.loads(reply)

print("\n========== 分析报告 ==========")
print(json.dumps(report, ensure_ascii=False, indent=2))

with open("analysis_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("\n报告已存为 analysis_report.json")