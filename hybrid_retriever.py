from rank_bm25 import BM25Okapi
from langchain_core.documents import Document
from reranker import Reranker
from config import (
    MAX_DISTANCE,
    FINAL_TOP_K
)
import jieba

def tokenize_text(text):

    stopwords = {"的",
        "了",
        "是",
        "什么",
        "怎么",
        "如何",
        "吗",
        "呢",
        "啊",
        "有",
        "和",
        "与",
        "在",
        "对",
        "请",
        "一下",
        "？",
        "?",
        "。",
        "，",
        ",",
        "！",
        "!"
    }

    text = text.strip().lower()

    raw_tokens = [
        token.strip()
        for token in jieba.lcut(text)
        if token.strip()
    ]

    tokens = []

    # 1.保留正常有效词
    for token in raw_tokens:

        if token not in stopwords:
            tokens.append(token)

    # 2.对相邻中文词做有限组合
    for i in range(len(raw_tokens) - 1):

        left = raw_tokens[i]
        right = raw_tokens[i + 1]

        # 两边都必须包含中文
        if (
            any("\u4e00" <= c <= "\u9fff" for c in left)
            and any("\u4e00" <= c <= "\u9fff" for c in right)
        ):
            combined = left + right

            # 组合长度控制
            if 2 <= len(combined) <= 6:
                tokens.append(combined)

    # 3.去重，保持原顺序
    tokens = list(
        dict.fromkeys(tokens)
    )

    return tokens

def reciprocal_rank_fusion(
        vector_results,
        bm25_results,
        k = 60
):
    """
    RRF融合
    k: 平滑参数，避免排名靠前权重过大
    """

    fused_scores = {}

    # 向量检索排名
    for rank, item in enumerate(vector_results):

        # 防止嵌套tuple，拆包
        if isinstance(item, tuple):
            doc = item[0]
        else:
            doc = item
        
        # 如果不加"未知"，出错会报错keyerror，加上后会返回默认值"未知"
        doc_id = doc.metadata.get(
            "chunk_id",
            "未知"
        )

        # 第一次遇到文档，初始化条目；后面再次遇到就累加score，最终按照score排序
        if doc_id not in fused_scores:
            # 如果这个文档还没有加入融合结果，就创建一个新的条目，避免同一个文档在多个检索结果中重复累计前先被初始化
            fused_scores[doc_id] = {
                "doc": doc,
                "score": 0
            }

        # 取两次字典
        fused_scores[doc_id]["score"] += (1 / (k + rank + 1))

    # BM25排名
    for rank, item in enumerate(bm25_results):
                    # 这里doc.metadata认为doc.metadata是Document对象，但实际是元组
        if isinstance(item, tuple):
            doc = item[0]
        else:
            doc = item
            
        doc_id = doc.metadata.get(
            "chunk_id",
            rank
        )

        if doc_id not in fused_scores:
            fused_scores[doc_id] = {
                "doc": doc,
                "score": 0
            }
        
        fused_scores[doc_id]["score"] += (1 / (k + rank + 1))

    # 按RRF分数降序
    fused_results = sorted(
        fused_scores.values(),
        # 传给sorted()的key参数是一个函数,这个函数对每个元素x返回它的score值
        key = lambda x:x["score"],
        # True表示从大到小
        reverse = True
    )

    return [
        (
            item["doc"],
            item["score"]
        )
        for item in fused_results
    ]

class HybridRetriever:

    def __init__(self, vectorstore):
        # 加载 Chroma
        self.vectorstore = vectorstore

        # 获取所有文本
        data = vectorstore.get(
            # 只返回这两个部分，不取其他的字段
            include = ["documents", "metadatas"]
        )

        # 用列表推导式把这对列表转换成一个新的文档对象列表
        self.documents = [
            # 为每一对text和metadata创建一个document对象
            Document(
                page_content = text,
                metadata = metadata
            )
                                # 按索引一一配对得到元组
            for text, metadata in zip(
                # 文本列表
                data["documents"],
                # 元数据列表
                data["metadatas"]
            )
        ]

        # BM25需要分词
        tokenized_docs = [
            tokenize_text(doc.page_content)
            for doc in self.documents
        ]

        # 对self.documents中文本做关键词检索，给每个文档一个BM25分数，分数和向量检索结果融合，提高检索效果
        self.bm25 = BM25Okapi(
            tokenized_docs
        )

        self.reranker = Reranker()

    def search(
            self,
            question,
            k = 5,
            # 正常rag时不传这个参数，和以前一样只返回最终Reranker结果。消融评估调用就改为True，同时返回Chroma、RRF、Reranker
            return_stages = False
            ):
        # 向量检索
        vector_results = (
                            # similarity_search_with_score()返回的是元组
            self.vectorstore.similarity_search_with_score(
                question,
                k = k
            )
        )

        print("\n========== Chroma原始候选结果(过滤前) ==========")

        for rank, (doc, distance) in enumerate(
            vector_results,
            start=1
        ):
            print(
                f"排名:{rank}, "
                f"distance:{distance:.4f}, "
                f"chunk_id:{doc.metadata.get('chunk_id')}, "
                f"内容:{doc.page_content[:100]}"
            )

        vector_results = [
            (doc, distance)
            for doc, distance in vector_results
            if distance <= MAX_DISTANCE
        ]

        if len(vector_results) == 0:

            if return_stages:
                return{
                    "chroma": [],
                    "rrf": [],
                    "reranker": []
                }

            return []

        # BM25
        query_tokens = tokenize_text(question)

        scores = self.bm25.get_scores(
            query_tokens
        )

        print("\n========== BM25查询分词 ==========")
        print(query_tokens)

        # 先计算 bm25_ids
        bm25_ids = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:k]

        # 再打印
        print("\n========== BM25 Top结果 ==========")
        
        for rank, i in enumerate(
            bm25_ids,
            start=1
        ):
            print(
                f"排名:{rank}, "
                f"BM25分数:{scores[i]:.4f}, "
                f"chunk_id:{self.documents[i].metadata.get('chunk_id')}, "
                f"内容:{self.documents[i].page_content[:100]}"
            )

        max_score = max(scores) if max(scores) > 0 else 1

        bm25_results = [
            (
                self.documents[i],
                1 - scores[i] / max_score
            )
            for i in bm25_ids
        ]

        fused_results = reciprocal_rank_fusion(
            vector_results,
            bm25_results
        )

        print("\n========== RRF最终结果 ==========")

        for rank, (doc, score) in enumerate(
            fused_results[:k],
            start=1
        ):
            print(
                f"排名:{rank}, "
                f"RRF分数:{score:.4f}, "
                f"chunk_id:{doc.metadata.get('chunk_id')}, "
                f"内容:{doc.page_content[:100]}"
            )

        reranked_results = self.reranker.rerank(
            question = question,
            documents_with_scores = fused_results[:k],
            top_k = FINAL_TOP_K
        )

        print("\n=========Reranker最终结果===========")

        for rank, (doc, reranker_score, rrf_score) in enumerate(reranked_results, start = 1):
            print(
                f"排名:{rank},"
                f"Reranker分数:{reranker_score:.4f},"
                f"原RRF分数:{rrf_score:.4f},"
                f"chunk_id:{doc.metadata.get('chunk_id')},"
                f"内容:{doc.page_content[:100]}"

            )

        final_results = [
            (
                doc,
                reranker_score
            )
            for (
                doc,
                reranker_score,
                rrf_score
            ) in reranked_results
        ]

        if return_stages:
            return {
                "chroma": vector_results,
                "rrf": fused_results[:k],
                "reranker": final_results
            }

        return final_results


