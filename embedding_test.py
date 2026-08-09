from sentence_transformers import SentenceTransformer
import numpy as np

# 加载模型（第一次运行会自动下载，之后从本地读取）
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def get_embedding(text):
    return model.encode(text)

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# 测试文字：中英德混合，故意放几组"意思像"和"意思不像"的
texts = {
    "猫": get_embedding("猫"),
    "狗": get_embedding("狗"),
    "股票": get_embedding("股票"),
    "登录失败": get_embedding("登录失败"),
    "无法访问账户": get_embedding("无法访问账户"),
    "Login fehlgeschlagen": get_embedding("Login fehlgeschlagen"),  # 德语"登录失败"
}

# 看一眼向量长什么样、多少维
print("「猫」的向量前5个数字:", texts["猫"][:5])
print("向量维度:", len(texts["猫"]))
print()

# 两两比较相似度
pairs = [
    ("猫", "狗"),
    ("猫", "股票"),
    ("登录失败", "无法访问账户"),
    ("登录失败", "Login fehlgeschlagen"),   # 跨语言！中文vs德语
    ("登录失败", "猫"),
]

for a, b in pairs:
    sim = cosine_similarity(texts[a], texts[b])
    print(f"「{a}」 vs 「{b}」 → 相似度: {sim:.3f}")

