from sentence_transformers import SentenceTransformer
import chromadb
from documents import DOCS

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def chunk_text(text, chunk_size=200, overlap=50):
    """
    把长文本切成固定长度的小块，块之间有重叠。
    text: 原始文本
    chunk_size: 每块多少个字符
    overlap: 相邻块重叠多少个字符
    返回: 一个 list，每个元素是一小段文字
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start: end]
        chunks.append(chunk)
        start = start + (chunk_size - overlap)

    return chunks
    pass

# 测试一下你的 chunking 函数（先跑这一段，看切得对不对）
if __name__ == "__main__":
    # 第1步：把4篇文档全部切块，同时记住每块来自哪篇文档
    all_chunks = []      # 存文字
    all_ids = []         # 存每块的唯一编号
    all_metadata = []    # 存每块的来源信息（哪篇文档、标题）

    for doc in DOCS:
        doc_chunks = chunk_text(doc["text"])
        for i, chunk in enumerate(doc_chunks):
            all_chunks.append(chunk)
            all_ids.append(f"{doc['id']}_chunk{i}")           # 比如 "doc1_chunk0"
            all_metadata.append({"title": doc["title"], "doc_id": doc["id"]})

    print(f"总共切出 {len(all_chunks)} 个chunk")

    # 第2步：建一个 ChromaDB 数据库（存在本地文件夹里）
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection("it_support_docs")

    # 第3步：把所有chunk转成向量，存进去
    embeddings = model.encode(all_chunks).tolist()   # 批量转向量
    collection.add(
        ids=all_ids,
        embeddings=embeddings,
        documents=all_chunks,
        metadatas=all_metadata
    )
    print("已存入 ChromaDB")

    # 第4步：测试检索——提一个问题，看能不能找到相关的chunk
    # 第4步：多个测试问题，验证检索准确率
    test_queries = [
        "Nutzer bekommt MFA Fehler beim Login",           # 应该命中 doc1 (Login)
        "Warum wurde ich doppelt abgerechnet?",            # 应该命中 doc2 (Abrechnung)
        "SharePoint lädt sehr langsam",                     # 应该命中 doc3 (SharePoint)
        "Kann ich beim Vertrag noch verhandeln?",           # 应该命中 doc4 (Vertrag)
        "Was ist das Wetter heute in Frankfurt?",           # 不相关问题，看系统怎么处理
    ]

    for query in test_queries:
        query_embedding = model.encode(query).tolist()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=1   # 只看最相关的1个，方便快速核对
        )

        print(f"\n{'='*50}")
        print(f"问题: {query}")
        top_doc = results["documents"][0][0]
        top_meta = results["metadatas"][0][0]
        top_distance = results["distances"][0][0]
        print(f"命中文档: {top_meta['title']} (距离: {top_distance:.3f})")
        print(f"内容: {top_doc[:100]}...")