# 程序正式启动前检查.env中是否有必要变量，docs文件夹是否存在，chroma_db是否存在，chroma_db是否为空

import os

from dotenv import load_dotenv

from config import DOCS_DIR, CHROMA_DIR
from logger import logger

def check_environment_variables():
    load_dotenv()

    required_variables = [
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "OPENAI_MODEL"
    ]

    missing_variables = []

    for variable_name in required_variables:
                        # os.getenv()读取环境变量，没有返回None
        variable_value = os.getenv(variable_name)

        if not variable_value:
            missing_variables.append(variable_name)
    
    if missing_variables:
        # 用日志系统输出一条错误级别的消息，里面的内容是缺少环境变量:missing_variables
        logger.error(
            f"缺少环境变量: {missing_variables}"
        )
        return False
    
    logger.info("环境变量检查通过")
    return True

def check_docs_directory():
    # os.path.exists()判断路径是不是一个存在的文件夹
    if not os.path.exists(DOCS_DIR):
        logger.error(
            f"资料文件夹不存在: {DOCS_DIR}"
        )
        return False
    
    # os.path.isdir()进一步判断是不是文件夹
    if not os.path.isdir(DOCS_DIR):
        logger.error(
            f"{DOCS_DIR}存在，但它不是文件夹"
        )
        return False
    
    logger.info("资料文件夹检查通过")
    return True

def check_vector_database():
    if not os.path.exists(CHROMA_DIR):
        logger.error(
            f"向量数据库不存在: {CHROMA_DIR}"
        )
        logger.error(
            "请先运行python build_vector_db.py"
        )
        return False
    
    if not os.path.isdir(CHROMA_DIR):
        logger.error(
            f"{CHROMA_DIR}存在，但它不是文件夹"
        )
        return False
    
    # os.listdir()获取该文件夹中的内容，下面代码表示这个文件夹为空
    if len(os.listdir(CHROMA_DIR)) == 0:
        logger.error("向量数据库文件夹为空")
        return False
    
    logger.info("向量数据库检查通过")
    return True

# 只为了检查环境变量和docs，不要求chroma_db存在
def run_health_check(require_vector_db = True):
    logger.info("开始运行启动检查")

    environment_ok = check_environment_variables()
    docs_ok = check_docs_directory()

    vector_db_ok = True

    if require_vector_db:
        vector_db_ok = check_vector_database()

    # 只有三个值全为True时，结果才为True
    all_checks_passed = (
        environment_ok
        and docs_ok
        and vector_db_ok
    )

    if all_checks_passed:
        logger.info("所有启动检查均已通过")
    else:
        logger.error("启动检查未通过")

    return all_checks_passed