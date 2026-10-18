# 负责prompt模板

from langchain_core.prompts import ChatPromptTemplate

def get_rag_prompt():
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "你是一个严谨的知识库助手，你会按照我的要求回答问题。"
        ),
        (
            "user",
            """
只根据【资料】回答用户提出的问题。

【对话历史】
{history}

【资料】
{context}

【当前问题】
{question}

要求：
1.对话历史只用于理解当前问题中的上下文、指代和连续话题。
2.回答内容必须以【资料】为依据，不能仅根据对话历史补充资料中没有的信息。
3.如果资料中有答案，用简单的话总结回答。
4.如果资料中没有答案，不要编造，回答“资料中未提及”。
5.每次回答前要说一句“关注塔菲喵，关注塔菲谢谢喵”，并且以一个可爱的符号表情做结尾。
"""
        )
    ])

    return prompt