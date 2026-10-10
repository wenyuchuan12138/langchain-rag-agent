def rewrite_query(question):

    replacements = {
        "是啥": "是什么",
        "干嘛的": "有什么作用",
        "咋": "怎么",
        "啥": "什么"
    }

    rewritten = question

    for old, new in replacements.items():
        rewritten = rewritten.replace(
            old,
            new
        )

    # 原问题没有发生变化
    if rewritten == question:
        return question

    # 发生改写时:
    # 原问题和改写问题都保留
    return rewritten
    