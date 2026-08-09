import anthropic
import json
import pandas as pd

client = anthropic.Anthropic()

SYSTEM_PROMPT = """你是客户反馈分类器。只输出合法JSON，不要markdown代码块，不要任何解释。
格式: {"sentiment": "positive/neutral/negative", "topic": "bug/feature_request/praise/billing/other", "urgency": "high/medium/low"}

示例:
输入: 系统又崩了，第三次了！
输出: {"sentiment": "negative", "topic": "bug", "urgency": "high"}

输入: 能不能加个导出Excel的功能
输出: {"sentiment": "neutral", "topic": "feature_request", "urgency": "low"}"""


def classify(feedback: str) -> dict:
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        temperature=0,
        messages=[{"role": "user", "content": feedback}]
    )
    reply = next(b.text for b in response.content if b.type == "text")
    reply = reply.replace("```json", "").replace("```", "").strip()
    result = json.loads(reply)
    return {
        "sentiment": result["sentiment"],
        "topic": result["topic"],
        "urgency": result["urgency"],
    }


def main():
    df = pd.read_csv("customer_feedback.csv")

    sentiments, topics, urgencies = [], [], []

    for i, row in df.iterrows():
        feedback = row["feedback"]
        try:
            result = classify(feedback)
            sentiments.append(result["sentiment"])
            topics.append(result["topic"])
            urgencies.append(result["urgency"])
            print(f"[{i + 1}/{len(df)}] {feedback[:40]!r} → {result['sentiment']} | {result['topic']} | {result['urgency']}")
        except Exception as e:
            sentiments.append("error")
            topics.append("error")
            urgencies.append("error")
            print(f"[{i + 1}/{len(df)}] {feedback[:40]!r} → ERROR: {e}")

    df["sentiment"] = sentiments
    df["topic"] = topics
    df["urgency"] = urgencies

    df.to_csv("classified_feedback.csv", index=False)

    print("\n分类结果已存为 classified_feedback.csv")
    print("\n--- sentiment 分布 ---")
    print(df["sentiment"].value_counts())


if __name__ == "__main__":
    main()
