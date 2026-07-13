# 负责读取docs文件夹的资料

import os
import pandas as pd

from langchain_community.document_loaders import TextLoader
# from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import CSVLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from document_parser import parser_pdf_with_mineru

from config import DOCS_DIR, CHUNK_SIZE, CHUNK_OVERLAP, SUPPORTED_EXTENSIONS

def load_txt_or_md(file_path):
    loader = TextLoader(file_path, encoding = "utf-8")
    documents = loader.load()

    for doc in documents:
        doc.metadata["file_type"] = "text"

    return documents

def load_pdf(file_path):

    markdown_path = parser_pdf_with_mineru(file_path)

    if not markdown_path:
        raise Exception("Mineru解析失败,没有生成Markdown文件")

    loader = TextLoader(
        markdown_path,
        encoding = "utf-8"
    )

    documents = loader.load()

    for doc in documents:
        doc.metadata.update({
            "file_type": "pdf",
            "parser": "mineru",
            "source_file": file_path
        })

    return documents

def load_docx(file_path):
    loader = Docx2txtLoader(file_path)
    documents = loader.load()

    for doc in documents:
        doc.metadata["file_type"] = "docx"

    return documents

def load_csv(file_path):
    loader = CSVLoader(file_path, encoding = "utf-8")
    documents = loader.load()

    for doc in documents:
        doc.metadata["file_type"] = "csv"

    return documents

def load_xlsx(file_path):
    df = pd.read_excel(file_path)

    documents = []
                    # 逐行遍历表格
    for index, row in df.iterrows():
                # 把表格中的一行转成字符串
        row_text = row.to_string()

        doc = Document(
            page_content = row_text,
            metadata = {
                "source": file_path,
                "file_type": "xlsx",
                "row_index": index + 1 
            } 
        )

        documents.append(doc)
    
    return documents

def load_single_file(file_path):
           # 把文件路径拆成文件主体和后缀
    _, ext = os.path.splitext(file_path)
    # 统一转换成小写
    ext = ext.lower()

    if ext == ".txt" or ext == ".md":
        return load_txt_or_md(file_path)
    
    elif ext == ".pdf":
        return load_pdf(file_path)
    
    elif ext == ".docx":
        return load_docx(file_path)
    
    elif ext == ".csv":
        return load_csv(file_path)
    
    elif ext == ".xlsx":
        return load_xlsx(file_path)
    
    else:
        return[]

def load_documents():
    documents = []
                     # 列出文件夹中所有文件名
    for filename in os.listdir(DOCS_DIR):
        file_path = os.path.join(DOCS_DIR, filename)
             # 判断这个路径是不是文件
        if not os.path.isfile(file_path):
            continue

        _, ext = os.path.splitext(filename)
        ext = ext.lower()

        if ext not in SUPPORTED_EXTENSIONS:
            print(f"跳过不支持的文件：{filename}")
            continue

        print(f"正在读取文件：{filename}")

        file_documents = load_single_file(file_path)

        documents.extend(file_documents)

    return documents

def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = CHUNK_SIZE,
        chunk_overlap = CHUNK_OVERLAP,
        separators = [
            "\n# ",
            "\n## ",
            "\n### ",
            "\n\n",
            "\n",
            "。",
            "！",
            "？",
            ""
        ]
    )

    chunks = text_splitter.split_documents(documents)

    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = index + 1
    
    return chunks