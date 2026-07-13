import hashlib
import json
import shutil
from pathlib import Path

from config import (
    INCOMING_DIR,
    PROCESSED_DIR,
    FAILED_DIR,
    MANIFEST_FILE,
    SUPPORTED_EXTENSIONS
)

from loaders import load_single_file, split_documents
from logger import logger
from vector_db import (
    add_documents_to_vector_db,
    delete_documents_from_vector_db
)

# ensure_directories()确保三个文件夹存在，不存在就创建
def ensure_directories():
    Path(INCOMING_DIR).mkdir(exist_ok = True)
    Path(PROCESSED_DIR).mkdir(exist_ok = True)
    Path(FAILED_DIR).mkdir(exist_ok = True)

def calculate_file_hash(file_path):
    # 创建SHA-256哈希计算器，只要内容发生改变哈希就会变化
    sha256 = hashlib.sha256()

                        # rb按二进制读取，方便统一计算哈希
    with open(file_path, "rb") as file:
        while True:
            # 分块读取文件，每次读取1mb
            data = file.read(1024 * 1024)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()

def load_manifest():
    manifest_path = Path(MANIFEST_FILE)

    if not manifest_path.exists():
        return {}
    
    with open(
        manifest_path,
        "r",
        encoding = "utf-8"
    )as file:
            # 读取清单
        return json.load(file)
    
def save_manifest(manifest):
    with open(
        MANIFEST_FILE,
        "w",
        encoding = "utf-8"
    )as file:
        # 保存清单
        json.dump(
            # 写入json的python对象
            manifest,
            # 已打开的文件对象，json.dump会把json文本写入这个文件
            file,
            # False直接写入中文和其他Unicode字符
            ensure_ascii = False,
            # 指定json缩进空格数
            indent = 2
        )

def create_chunk_ids(file_hash, chunks):
    ids = []

    for index, chunk in enumerate(chunks, start = 1):
        chunk_id = (f"{file_hash}_chunk_{index}")

        # metadata是每个文本块chunk对象自带的一个字典，用于保存该文本块相关的额外信息
        # chunk是对象，chunk.page_content是文本内容，chunk.metadate是字典
        chunk.metadata["vector_id"] = chunk_id
        ids.append(chunk_id)

    return ids

# 处理一个待入库文件，并把它增量写入向量库
                # file_path待处理文件的路径对象 manifest当前内存中清单字典，用来记录已处理文件的哈希和chunk_id
def process_file(file_path, manifest):
    # 待处理文件名
    file_name = file_path.name
    # 待处理文件内容哈希
    file_hash = calculate_file_hash(file_path)

    # 取出旧记录
    old_record = manifest.get(file_name)

    if old_record:
        # 取出旧哈希
        old_hash = old_record.get("file_hash")

        if old_hash == file_hash:
            logger.info(f"文件未发生变化，跳过: {file_name}")

            return "skipped"
        
        # 如果文件更新，用旧chunk_ids调用delete_documents_from_vector_db()删除旧向量
        old_ids = old_record.get("chunk_ids", [])
        
        logger.info(f"检测到文件更新，删除旧向量: {file_name}")

        delete_documents_from_vector_db(old_ids)

    # 取出文件内容
    documents = load_single_file(str(file_path))

    if len(documents) == 0:
        raise ValueError(f"文件没有读取到内容: {file_name}")
    
    chunks = split_documents(documents)

    for chunk in chunks:
        chunk.metadata["original_file"] = file_name
        chunk.metadata["file_hash"] = file_hash

    chunk_ids = create_chunk_ids(file_hash, chunks)

    added_count = add_documents_to_vector_db(
        documents = chunks,
        ids = chunk_ids
    )

    manifest[file_name] = {
        "file_hash": file_hash,
        "chunk_ids": chunk_ids,
        "chunk_count": len(chunks)
    }

    logger.info(
        f"文件入库成功: {file_name},"
        f"新增{added_count}个文本块"
    )

    return "added"

def move_file(file_path, target_dir):
    target_path = Path(target_dir) / file_path.name

    if target_path.exists():
                    # unlink()删除文件,path.unlink() = os.remove()   
        target_path.unlink()

    # 把文件从incoming/移动到processed/
    # shutil.move(), shutil.copy2("c:/tmp/a.txt", "c:/dest/a.txt")复制并尽量保留元数据, shutil.rmtree("c:/temp/some_dir")删除整个目录树
    shutil.move(
        str(file_path),
        str(target_path)
    )

def main():
    ensure_directories()

    manifest = load_manifest()

    incoming_path = Path(INCOMING_DIR)

    files = [
        file_path
                                    # path.iterdir()遍历文件夹中的直接子项，类似于os.listdir()，但返回path对象
        for file_path in incoming_path.iterdir()
        if(
            file_path.is_file()
            and file_path.suffix.lower()
            in SUPPORTED_EXTENSIONS
        )
    ]

    if len(files) == 0:
        logger.info("incoming 文件夹中没有待入库文件")
        return
    
    for file_path in files:
        try:
            logger.info(f"开始处理新增文件: {file_path.name}")

            status = process_file(file_path = file_path, manifest = manifest)

            if status in ["added", "skipped"]:
                move_file(file_path, PROCESSED_DIR)

        except Exception as error:
            logger.exception(
                f"增量入库失败:"
                f"{file_path.name}, {error}"
            )

            move_file(
                file_path,
                FAILED_DIR
            )

    save_manifest(manifest)

    logger.info("增量入库任务完成")

if __name__ == "__main__":
    main()