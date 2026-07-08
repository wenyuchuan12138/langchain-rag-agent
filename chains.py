# 负责问答链
# retrieve_documents()负责检索向量数据库，根据分数过滤，整理来源信息，返回RetruevalResult
# fomat_context()负责把多个document的正文拼接成传给模型的从context
# answer_question负责调用检索函数，判断检索状态，调用大模型，返回AnswerResult

import os
import time
from pathlib import Path

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

from config import (
    TOP_K,
    MAX_DISTANCE,
    LLM_TIMEOUT,
    MAX_RETRIES,
    RETRY_BASE_DELAY
)

from exceptions import (
    RetrievalError,
    RetryableModelError,
    NonRetryableModelError
)

from logger import logger
from vector_db import load_vectorstore
from prompts import get_rag_prompt
from schemas import(
    SourceInfo,
    RetrievalResult,
    AnswerResult
)

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model = os.getenv("OPENAI_MODEL")

def get_llm():
    llm = ChatOpenAI(
        api_key = api_key,
        base_url = base_url,
        model = model,
        # 生成答案的随机性
        temperature = 0,
        timeout = LLM_TIMEOUT,
        # 表示先关闭模型对象内容的自动重试，手动控制重试过程
        max_retries = 0
    )

    return llm

vectorstore = load_vectorstore()

llm = get_llm()
prompt = get_rag_prompt()
parser = StrOutputParser()

answer_chain = prompt | llm | parser

def retrieve_documents(question):
            # time.pref_counter()从开始到现在经过多长时间，time.time()看当前时刻是什么时间,
    start_time = time.perf_counter()

    # 把可能出错的代码放进去执行，出错时执行except Exception
    try:
        logger.info(
            f"开始检索资料，问题:{question}"
        )

        results = (
            vectorstore.similarity_search_with_score(
                question,
                k = TOP_K
            )
        )

        filtered_documents = []
        source_list = []

        for doc, score in results:
            if score <= MAX_DISTANCE:
                filtered_documents.append(
                    (doc, score)
                )

                source_info = SourceInfo(
                    source = doc.metadata.get(
                        "chunk_id",
                        "未知来源"
                    ),
                    chunk_id = doc.metadata.get(
                        "chunk_id",
                        "未知块"
                    ),
                    # 返回分数不一定是标准python
                    score = float(score)
                )

                source_list.append(source_info)

        retrieval_time = (
            time.perf_counter() - start_time
        )

        if len(filtered_documents) == 0:
            logger.warning(
                "没有检索到满足阈值的资料"
            )

            return RetrievalResult(
                success = True,
                documents = [],
                sources = [],
                message = "资料中未提及。",
                retrieval_time = retrieval_time
            )
        
        logger.info(
            f"检索完成，保留"
            f"{len(filtered_documents)}条资料,"
            f"耗时{retrieval_time:.4f}秒"
        )

        # 检索成功时，是一个对象可通过retrieval_result.success获取是否成功
        return RetrievalResult(
            # 这里的True是指的程序运行正常，而不是是否找到资料
            success = True,
            documents = filtered_documents,
            sources = source_list,
            message = "检索成功",
            retrieval_time = retrieval_time
        )
    
    except Exception as error:
        retrieval_time = (
            time.perf_counter() - start_time
        )

        logger.exception(
            f"资料检索失败:{error}"
        )

        return RetrievalResult(
            success = False,
            documents = [],
            sources = [],
            message = str(error),
            retrieval_time = retrieval_time
        )
    
def format_context(documents_with_scores):
    context_list = []

    for doc, score in documents_with_scores:
        context_list.append(
            doc.page_content
        )
    
    return "\n\n".join(context_list)

def answer_question(question):
    total_start_time = time.perf_counter()

    retrieval_result = retrieve_documents(question)

    if not retrieval_result.success:
        total_time = (
            time.perf_counter() - total_start_time
        )

        return AnswerResult(
            success = False,
            answer = "",
            sources = [],
            error = (
                "检索资料时发生错误:" + retrieval_result.message
            ),
            retrieval_time = retrieval_result.retrieval_time,
            generation_time = 0.0,
            total_time = total_time
        )
    
    if len(retrieval_result.documents) == 0:
        total_time = (time.perf_counter() - total_start_time)

        return AnswerResult(
            success = True,
            answer = "资料中未提及。",
            sources = [],
            error = "",
            retrieval_time = retrieval_result.retrieval_time,
            total_time = total_time
        )
    
    context = format_context(
        retrieval_result.documents
    )

    generation_strat_time = (
        time.perf_counter()
    )

    try:
        logger.info("开始调用大模型生成答案")

        answer, retry_count = (
            generate_answer_with_retry(
                context = context,
                question = question
            )
        )

        generation_time = (time.perf_counter() - generation_strat_time)

        total_time = (time.perf_counter() - total_start_time)

        logger.info(
            f"模型回答完成，"
            f"生成耗时{generation_time:.4f}秒,"
            f"总耗时{total_time:.4f}秒"
        )

        return AnswerResult(
            success = True,
            answer = answer,
            sources = retrieval_result.sources,
            error = "",
            retrieval_time = retrieval_result.retrieval_time,
            generation_time = generation_time,
            total_time = total_time,
            retry_count = retry_count,
            used_fallback = False
        )
    
    except NonRetryableModelError as error:
        generation_time = time.perf_counter() - generation_strat_time
        total_time = time.perf_counter() - total_start_time
        logger.exception(f"模型发生不可重试错误:{error}")

        return AnswerResult(
            success = False,
            answer = "",
            sources = retrieval_result.sources,
            error =  str(error),
            retrieval_time = (retrieval_result.retrieval_time),
            generation_time = generation_time,
            total_time = total_time,
            retry_count = 0,
            uesd_fallback = False
        )
    
    except RetryableModelError as error:
        generation_time = time.perf_counter() - generation_strat_time
        total_time = time.perf_counter() - total_start_time
        fallback_answer = build_fallback_answer(retrieval_result.documents) 

        logger.warning("模型多次重试失败,使用检索资料兜底")

        return AnswerResult(
            # 降级服务，仍旧有内容设置True
            success = True,
            answer = fallback_answer,
            sources = retrieval_result.sources,
            error = str(error),
            retrieval_time = retrieval_result.retrieval_time,
            generation_time = generation_time,
            total_time = total_time,
            retry_count = MAX_RETRIES - 1,
            uesd_fallback = True   
        )

# 输入一个原始异常，根据错误里包含什么，返回RetryableModelError或者NoneRetryableModelError
def classify_model_error(error):
    error_text = str(error).lower()

    retryable_keywords = [
        "timeout",
        "time out",
        "connection",
        "temporarily unavailable",
        "rate limit",
        "429",
        "500",
        "502",
        "503",
        "504"
    ]

    non_retryable_keywords = [
        "api key",
        "authentication",
        "unauthorized",
        "401",
        "invalid model",
        "model not found",
        "bad request",
        "400"
    ]

    for keyword in non_retryable_keywords:
        if keyword in error_text:
            return NonRetryableModelError(
                str(error)
            )
        
    for keyword in retryable_keywords:
        if keyword in error_text:
            return RetryableModelError(
                str(error)
            )
        
    # 未知错误默认不重试
    return NonRetryableModelError(
        str(error)
    )

def calculate_retry_delay(attempt_number):
    delay = (
        # RETRY_BASE_DELAY乘上2的attempt_number次方
        RETRY_BASE_DELAY * (2 ** attempt_number)
    )

    return delay

def generate_answer_with_retry(
        context,
        question
):
    last_error = None
                
                # 分别对应第一次到第三次调用，但得到是0，1，2
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(
                f"开始第{attempt + 1}次模型调用"
            )

            answer = answer_chain.invoke({
                "context": context,
                "question": question
            })

            # 如果attempt = 0表示第一次调用就成功没有重试1表示第二次调用成功，重试1次
            retry_count = attempt

            logger.info({
                f"第{attempt + 1}次调用模型成功"
            })

            return answer, retry_count
        
        except Exception as original_error:
            classified_error = (
                classify_model_error(
                    original_error
                )
            )

            last_error = classified_error

            # isinstance判断一个对象是不是某个类型
            if isinstance(
                classified_error,
                NonRetryableModelError
            ):
                logger.error(
                    "模型发生不可重试错误："
                    f"{classified_error}"
                )

                # 主动抛出异常，程序会停止当前函数，并进入外层对应的except
                raise classified_error
            
            is_last_attempt = (
                attempt == MAX_RETRIES - 1
            )

            if is_last_attempt:
                logger.error(
                    "模型重试次数已用尽"
                )

                raise classified_error
            
            delay = calculate_retry_delay(
                attempt
            )

            logger.warning(
                f"模型调用失败:"
                f"{classified_error};"
                f"{delay:1.f}秒后重试"
            )

            # 让当前程序暂停指定秒数
            time.sleep(delay)

    raise RetryableModelError(
        str(last_error)
    )

# 增加兜底答案函数,降级处理
def build_fallback_answer(
        documents_with_scores
):
    fallback_parts = [
        "大模型当前暂时无法生成答案,",
        "以下是知识库中检索到的相关原文:"
    ]

    for index, item in enumerate(
        documents_with_scores,
        start = 1
    ):
        doc = item[0]

        content = doc.page_content.strip()

        fallback_parts.append(
            f"\n【资料:{index}】\n"
            f"{content}"
        )

    return "\n".join(fallback_parts)