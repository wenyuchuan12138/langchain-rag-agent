def generate_multi_queries(question):

    queries = [question]

    if "作用" in question:
        new_query = question.replace(
            "有什么作用",
            "是什么"
        )

        queries.append(
            new_query
        )

    if "是什么" in question:
        new_query = question.replace(
            "是什么",
            "有什么作用"
        )

        queries.append(
            new_query
        )

    if "怎么" in question:
        new_query = question.replace(
            "怎么",
            "如何"
        )

        queries.append(
            new_query
        )

    # 去重，同时保持原顺序
    queries = list(
        dict.fromkeys(queries)
    )

    # 最多保留3个
    return queries[:3]