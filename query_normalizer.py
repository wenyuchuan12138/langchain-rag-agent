import re

def normalize_query(query):

    query = query.strip()

    # 合并连续空格
    query = re.sub(
        r"\s+",
        "",
        query
    )

    # 去掉连续重复标点
    query = re.sub(
        r"[?？]{2,}",
        "?",
        query
    )

    query = re.sub(
        r"[!！]{2,}",
        "!",
        query
    )

    # 英文统一小写
    query = query.lower()

    return query
    