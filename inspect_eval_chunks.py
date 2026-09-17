from chains import hybrid_retriever
from config import RETRIEVAL_TOP_K


questions = [
    "LangChain是什么？",
    "Embedding是什么？",
    "Agent是什么？",
    "向量库是什么？",
    "怎样让大模型利用外部资料回答问题？",
    "如何把文档转换成便于语义检索的表示？",
    "Embedding和向量库有什么区别？",
    "RAG和Agent有什么区别？",
    "苹果公司的股价是多少？",
    "今天天气怎么样？"
]


for question in questions:

    print(
        "\n\n"
        "===================================="
    )

    print(
        f"问题：{question}"
    )

    results = hybrid_retriever.search(
        question,
        RETRIEVAL_TOP_K
    )

    for rank, (doc, score) in enumerate(
        results,
        start=1
    ):
        print(
            f"\n排名：{rank}"
        )

        print(
            "chunk_id：",
            doc.metadata.get(
                "chunk_id",
                "unknown"
            )
        )

        print(
            "内容："
        )

        print(
            doc.page_content
        )

        print(
            f"分数：{score:.4f}"
        )