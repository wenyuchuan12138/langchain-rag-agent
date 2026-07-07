# 函数返回内容太多，在此统一规定回答函数返回

from dataclasses import dataclass, field
from typing import Any

# 自动生成__init__(),自动生成__repr__(),方便快速定义只存数据的类
# 表示这个类是一个数据类，主要用来存储结构化数据，避免返回一大堆字典
@dataclass
# 表示一条引用来源
class SourceInfo:
    # source是字符串 chunk_id是整数或字符串 score是浮点数
    source: str
    # chunk_id既可以是整数，也可以是字符串
    chunk_id: int | str
    score: float
# 上面的式子等价于python会自动生成一个初始化方法，与下列一致
# class SourceInfo:
#     def __init__(self, source: str, chunk_id: int | str, score: float):
#         self.source = source
#         self.chunk_id = chunk_id
#         self.score = score

@dataclass
# 表示检索阶段结果
class RetrievalResult:
    success: bool
    # documents是一个列表，内部可以放任意类型
    documents: list[Any] = field(default_factory = list)
    # 如果创建对象时没有传sources,就自动创建一个新的空列表,避免多个对象共用一个列表
    sources: list[SourceInfo] = field(default_factory = list)
    message: str = ""
    retrieval_time: float = 0.0

@dataclass
# 表示最终问答阶段结果
class AnswerResult:
    success: bool
    answer: str
    sources: list[SourceInfo] = field(default_factory = list)
    error: str = ""

    # 从向量库检索资料的时间
    retrieval_time: float = 0.0
    # 大模型生成答案的时间
    generation_time: float = 0.0
    # 整个问答过程耗时
    total_time: float = 0.0

    # 表示本次任务发生的几次重试，不包括第一次调用
    retry_count: int = 0
    # 表示大模型最终成功，True表示没有成功
    used_fallback: bool = False