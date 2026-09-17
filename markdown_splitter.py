from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter
)

from config import CHUNK_SIZE, CHUNK_OVERLAP

# 规定识别哪些Markdown标题
HEADERS_TO_SPLIT_ON = [
    ("#", "header_1"),
    ("##", "header_2"),
    ("###", "header_3"),
    ("####", "header_4")
]

def create_markdown_header_splitter():
    """
    创建Markdown标题切分器
    按照#、##、###、####切分文档
    """
            # 按照Markdown标题切分
    splitter = MarkdownHeaderTextSplitter(
        # headers_to_split_on规定识别哪些标题
        headers_to_split_on = HEADERS_TO_SPLIT_ON,
        # 表示切分后，不从正文中删除标题
        strip_headers = False
    )

    return splitter

def create_secondary_splitter():
    """
    创建二次字符切分器

    如果一个标题章节仍然过长
    再根据字符数量继续切分
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size = CHUNK_SIZE,
        chunk_overlap = CHUNK_OVERLAP,
        separators = [
            "\n\n",
            "\n",
            "。",
            "！",
            "？",
            "；",
            "，",
            " ",
            ""
        ]
    )

    return splitter

def merge_metadata(
        original_metadata,
        header_metadata
):
    """
    合并文档metadata和标题metadata
    """

    # 复制一份字典，直接merged_metadata = original_metadata可能导致修改一个会影响另一个
    merged_metadata = original_metadata.copy()

    # 把另一个字典中的字段加入当前字典
    merged_metadata.update(
        header_metadata
    )

    return merged_metadata

def split_single_markdown_document(document):
    """
    对一个MinerU Markdown文档进行结构化切分

    第一步:按Markdown标题切分
    第二步:对过长章节进行字符切分
    """

    header_splitter = create_markdown_header_splitter()

    # 吧Markdown字符串切成多个Document
    header_documents = (
        header_splitter.split_text(
            # 完整Markdown文本
            document.page_content
        )
    )

    #把原始文件来源等metadata合并到标题切分后的document中
    for header_document in header_documents:
        header_document.metadata = (
            merge_metadata(
                original_metadata = (
                    document.metadata
                ),
                header_metadata = (
                    header_document.metadata
                )
            )
        )
    
    # 过多字数形成一个向量或导致检索不够精准
    secondary_splitter = (
        create_secondary_splitter()
    )

    final_chunks = (
        secondary_splitter.split_documents(
            header_documents
        )
    )

    return final_chunks

def split_normal_documents(documents):
    """
    对非MinerU文档继续使用普通字符切分
    """

    if len(documents) == 0:
        return []
    
    normal_splitter = (
        create_secondary_splitter()
    )

    chunks = normal_splitter.split_documents(documents)

    return chunks

def split_mixed_documents(documents):
    """
    混合切分入口

    MinerU解析的PDF:使用Markdown结构切分
    TXT、Word、CSV、Excel等:使用普通字符切分
    """

    markdown_chunks = []
    normal_documents= []

    for document in documents:
        parser_name = document.metadata.get(
            "parser",
            ""
        )

        file_type = document.metadata.get(
            "file_type",
            ""
        )

        is_mineru_document = (
            parser_name == "MinerU"
            or file_type == "mineru_pdf"
        )

        if is_mineru_document:
            current_chunks = (
                split_single_markdown_document(document)
            )

            # extend会把[chunk1, chunk2, chunk3]逐一加入列表
            markdown_chunks.extend(current_chunks)

        else:
            normal_documents.append(document)

    normal_chunks = split_normal_documents(normal_documents)

    all_chunks = (markdown_chunks + normal_chunks)

    # 给最终所有文本块统一编号
    for index, chunk in enumerate(all_chunks, start = 1):
        chunk.metadata["chunk_id"] = index
    
    return all_chunks
