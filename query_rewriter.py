import re

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

    follow_up_patterns = [
        (
            r"^(.+?)缺点(?:呢)?[？?]?$",
            r"\1有什么缺点"
        ),
        (
            r"^(.+?)优点(?:呢)?[？?]?$",
            r"\1有什么优点"
        ),
        (
            r"^(.+?)作用(?:呢)?[？?]?$",
            r"\1有什么作用"
        ),
        (
            r"^(.+?)优势(?:呢)?[？?]?$",
            r"\1有什么优势"
        ),
        (
            r"^(.+?)问题(?:呢)?[？?]?$",
            r"\1有什么问题"
        ),
    ]

    for pattern, replacement in follow_up_patterns:
        rewritten = re.sub(
            pattern,
            replacement,
            rewritten
        )

    # 原问题没有发生变化
    if rewritten == question:
        return question

    return rewritten