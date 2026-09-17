import chromadb

client = chromadb.PersistentClient(
    path="chroma_db"
)

print(client.list_collections())

collection = client.get_collection(
    name="langchain"
)

print("向量总数:", collection.count())

result = collection.get(
    include=["documents", "metadatas"]
)

for i, (doc, metadata) in enumerate(
    zip(
        result["documents"],
        result["metadatas"]
    ),
    start=1
):
    print("=" * 80)
    print("序号:", i)
    print("metadata:", metadata)
    print("内容:", doc[:300])


result = collection.get(
    where={
        "original_file":
        "rag_langchain_knowledge_word.docx"
    },
    include=["documents", "metadatas"]
)

print("Word文本块数量:", len(result["documents"]))

for doc, metadata in zip(
    result["documents"],
    result["metadatas"]
):
    print(metadata)
    print(doc)
    print()