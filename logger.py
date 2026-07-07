# 监测logs文件夹，创建logger对象，设置日志级别，创建文件输出器，创建终端输出器，设置日志格式，把输出器交给logger
# logger时基础设施模块和config、vector_db\health_check一样不可单独运行,在第一次import时初始化，之后在整个python进行生命周期内共享，不需要重复执行

import logging
import os

from config import LOGS_DIR, LOG_FILE

def create_logger():
    # 先判断文件夹是否已经存在
    # if not os.path.exists(LOGS_DIR):   这里不再判断而是直接创建文件的原因在于顺序，该函数会先运行FileHandler，然后发现log不存在直接报错，不会轮到or.makedirs()
        # os.makedirs()创建文件夹，并且可以创建多层目录
    os.makedirs(LOGS_DIR, exist_ok = True)

    # 创建或获取一个日志对象
    logger = logging.getLogger("rag_project")
    # 设置最低日志级别为INFO，低于该级别会忽略也即DEBUG，其他会显示
    logger.setLevel(logging.INFO)

    # 避免多次执行create_logger()
    if logger.handlers:
        return logger
    
    # 把日志写入文件
    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding = "utf-8"
    )

    # 把日志输出到终端
    console_handler = logging.StreamHandler()

    # 规定日志输出格式为发生时间、日志级别、logger名称、具体信息
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # 把刚刚创建的日志格式应用到两个输出器
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 把日志输出到文件和终端
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = create_logger()
