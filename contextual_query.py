import re

def extract_topic(question):
    """
    从上一轮问题中提取的主要讨论对象。
    例如
    RAG是什么？   -> RAG
    LangChain有什么用？ -> LangChain
    Embedding怎么使用？ -> Embedding
    """

    if not question:
        return None

    question = question.strip()

    endings = [
        "是什么",
        "是啥",
        "是干嘛的",
        "有什么作用",
        "有什么用",
        "有什么",
        "怎么用",
        "如何使用",
        "怎么",
        "如何",
        "为什么",
        "为何",
    ]

    for ending in endings:
        if ending in question:
            topic = question.split(
                ending,
                1
            )[0].strip()

            invalid_topics = {
                "它",
                "这个",
                "这种",
                "这个技术",
                "这种技术",
                "这个方法",
                "这种方法",
                "这个模型",
                "这种模型",
            }

            if topic and topic not in invalid_topics:
                return topic

    return None

def contextualize_query(
    current_question,
    previous_question = None,
    current_topic = None
):
    """
    如果当前问题依赖上一轮上下文，
    就把代词替换成上一轮主题。

    否则保持当前问题不变。
    """

    if not previous_question:
        return current_question

    topic = extract_topic(
        previous_question
    )

    print(
        f"[上下文调试] previous_question = {previous_question}"
    )

    print(
        f"[上下文调试] 提取topic = {topic}"
    )

    if not topic:
        topic = current_topic

    if not topic:
        return current_question

    contextual_words = [
        "这个方法",
        "这种方法",
        "这个技术",
        "这种技术",
        "这个模型",
        "这种模型",
        "这个",
        "这种",
        "它",
    ]

    rewritten = current_question

    for word in contextual_words:

        if word in rewritten:
            rewritten = rewritten.replace(
                word,
                topic,
                1
            )

            return rewritten

    follow_up_prefixes = [
        "那",
        "那么",
        "还有",
        "再说说",
        "继续说说",
    ]

    for prefix in follow_up_prefixes:
        if rewritten.startswith(prefix):
            rewritten = rewritten[len(prefix):].strip()

            return topic + rewritten

    return current_question

