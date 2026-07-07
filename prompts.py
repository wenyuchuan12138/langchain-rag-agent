# 负责prompt模板

from langchain_core.prompts import ChatPromptTemplate

def get_rag_prompt():
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个严谨的知识库助手，你会按照我的要求回答问题。"),
        ("user", """
    只根据【资料】和【问题】回答用户提出的问题
         要求：
         1.每次回答前要说一句关注塔菲喵，关注塔菲谢谢喵，并且以一个可爱的符号表情做结尾
         2.如果资料中有答案，用简单的话总结回答
         3.没有的答案不要编造，回答资料中未提及

         【资料】
         {context}

         【问题】
         {question}
    """)
    ])

    return prompt