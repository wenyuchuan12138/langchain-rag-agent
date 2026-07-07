# 运行一次来构建知识库

import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from health_check import run_health_check
from loaders import load_documents, split_documents
from logger import logger
from vector_db import build_vector_db

def main():
    health_ok = run_health_check(
        requrie_vector_db = False
    )

    if not health_ok:
        logger.error("构建向量数据库前检查失败")
        return 
    
    # 尝试执行try中的代码，如果出现异常就进入except
    try:
        logger.info("开始读取知识库文件")

        documents = load_documents()
    

        if len(documents) == 0:
            logger.warning(
                "没有读取任何支持的文档"
            )
            return
        
        logger.info(
            f"读取文档数量:{len(documents)}"
        )

        chunks = split_documents(documents)

        logger.info(
            f"生成文本块数量:{len(chunks)}"
        )

        logger.info("开始构建向量数据库")

        build_vector_db(chunks)

        logger.info("向量数据库创建完成")

    except Exception as error:
        # logger.exception()除了记录文字之外还把完整traceback写入日志，必须在except中使用，相比loggger.error()只记录一句错误,其更具有排错价值
        logger.exception(
            f"构建向量数据库失败:{error}"
        )

# 只有当这个文件被直接运行时，才执行main()
if __name__ == "__main__":
    main()