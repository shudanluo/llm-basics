import anthropic
import json

client = anthropic.Anthropic()

feedbacks = [
    "新版界面好看多了，赞一个",
    "发票金额算错了，请尽快处理",
    "登录页面偶尔加载很慢",
]

for fb in feedbacks:
    response = client.messages.create(
        # model="claude-sonnet-5",
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system="""你是客户反馈分类器。只输出合法JSON，不要markdown代码块，不要任何解释。
格式: {"sentiment": "positive/neutral/negative", "topic": "bug/feature_request/praise/billing/other", "urgency": "high/medium/low"}

示例:
输入: 系统又崩了，第三次了！
输出: {"sentiment": "negative", "topic": "bug", "urgency": "high"}

输入: 能不能加个导出Excel的功能
输出: {"sentiment": "neutral", "topic": "feature_request", "urgency": "low"}"""
,
        temperature=0,
        messages=[{"role": "user", "content": fb}]
    )
    reply = next(b.text for b in response.content if b.type == "text")

    reply = reply.replace("```json", "").replace("```", "").strip()
    result = json.loads(reply)
    print(f"{fb} → {result['sentiment']} | {result['topic']} | {result['urgency']}")
 