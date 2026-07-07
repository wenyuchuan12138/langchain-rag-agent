# 问答运行

from chains import answer_question
from health_check import run_health_check
from logger import logger

# 只负责显示来源
def dispaly_sources(sources):
    if len(sources) ==0:
        return
    
    print("\n参考来源:")

    for index, source_info in enumerate(sources, start = 1):
        print(
            f"{index}."
            f"文件{source_info.source},"
            f"文本块:第{source_info.chunk_id}块,"
            f"距离分数:{source_info.score:.4f}"
        )

def display_timing(result):
    print("\n运行耗时:")

    print(
        f"检索耗时:"
        # 字典是result["answer"],对象是result.answer
        f"{result.retrieval_time:.4f}秒"
    )

    print(
        f"生成耗时:"
        f"{result.generation_time:.4f}秒"
    )

    print(
        f"总耗时:"
        f"{result.total_time:.4f}秒"
    )

def display_runtime_status(result):
    if result.retry_count > 0:
        print(
            f"\n模型重试次数:"
            f"{result.retry_count}"
        )

    if result.used_fallback:
        print(
            "\n提示:本次大模型调用失败,"
            "系统已使用知识库原文进行降级回答。"
        )

def main():
    health_ok = run_health_check(
        require_vector_db = True
    )

    if not health_ok:
        logger.error("RAG系统启动失败")
        return
    
    logger.info("RAG问答系统启动成gong")

    while True:
        question = input("输入问题,输入q退出:").strip()

        if question == "":
            print("请输入有效问题。")
            continue

        if question.lower() in ["q", "exit", "退出"]:
            logger.info("用户结束程序")
            print("程序退出。")
            break

        logger.info(
            f"收到用户问题:{question}"
        )

        result = answer_question(question)

        if result.success:
            print("\nAI回答:")
            print(result.answer)

            dispaly_sources(
                result.sources
            )

            display_timing(result)

            display_runtime_status(result)

            print()
        
        else:
            print("\n系统处理失败:")
            print(result.error)

            display_timing(result)

            print()

if __name__ == "__main__":
    main()