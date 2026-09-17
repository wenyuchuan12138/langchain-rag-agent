# test_markdown_splitter.py

from loaders import (
    load_documents,
    split_documents
)


documents = load_documents()

chunks = split_documents(documents)


print("原始Document数量：", len(documents))
print("切分后chunk数量：", len(chunks))


for index, chunk in enumerate(
    chunks[:10],
    start=1
):
    print("\n" + "=" * 60)
    print(f"第{index}个文本块")

    print("\n正文：")
    print(chunk.page_content[:500])

    print("\nmetadata：")
    print(chunk.metadata)