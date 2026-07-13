# 负责 embedding 和 Chroma 向量库

import os
import shutil

# 必须写在导入 HuggingFaceEmbeddings 之前
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# 强制使用本地缓存，不主动联网检查 HuggingFace
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from config import CHROMA_DIR, EMBEDDING_MODEL


def get_embeddings():
    # 创建 embedding 模型
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={
            "device": "cpu",
            # 只从本地加载模型，不联网
            "local_files_only": True
        },
        encode_kwargs={
            "normalize_embeddings": True
        }
    )

    return embeddings


def build_vector_db(chunks):
    # 如果旧的 chroma_db 存在，就删除旧库
    if os.path.exists(CHROMA_DIR):
        shutil.rmtree(CHROMA_DIR)

    embeddings = get_embeddings()

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )


def load_vectorstore():
    embeddings = get_embeddings()

    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings
    )

    return vectorstore

# 加载现有chroma向量库，将传入的文档列表documents追加到向量库中，并用ids作为每个文档的向量id，返回已添加文档数量
def add_documents_to_vector_db(documents, ids):
    vectorstore = load_vectorstore()

    # 把新的document列表加入到现有向量库中
    vectorstore.add_documents(
        documents = documents,
        ids = ids
    )

    return len(ids)

# 如果ids为空，直接返回，不做任何操作，否则加载现有chroma向量库，从向量库中删除对应ids的向量
def delete_documents_from_vector_db(ids):
    if not ids:
        return
    
    vectorstore = load_vectorstore()
    vectorstore.delete(ids = ids)