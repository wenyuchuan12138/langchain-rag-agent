import json
from pathlib import Path

from chains import hybrid_retriever
from config import RETRIEVAL_TOP_K

EVAL_FILE = Path("eval_cases.json")

def load_eval_cases():

    with open(
        EVAL_FILE,
        "r",
        encoding = "utf-8"
    )as file:

        return json.load(file)

def extract_chunk_ids(results):

    return [
        str(
            doc.metadata.get(
                "chunk_id",
                "unknown"
            )
        ).strip()
        for doc, score in results
    ]

def top1_hit(
        predicted_ids,
        expected_ids
):
    if len(predicted_ids) == 0:
        return 0 

    if predicted_ids[0] in expected_ids:
        return 1

    return 0

def hit_at_k(
        predicted_ids,
        expected_ids,
        k = 3
):
    top_k_ids = predicted_ids[:k]

    for chunk_id in top_k_ids:

        if chunk_id in expected_ids:
            return 1

    return 0

def recall_at_k(
        predicted_ids,
        expected_ids,
        k = 3 
):

    if len(expected_ids) == 0:
        return 0.0

    predicted_set = set(
        predicted_ids[:k]
    )

    expected_set = set(
        expected_ids
    )

    matched = (
        predicted_set
        & expected_set
    )

    return (
        len(matched)
        / len(expected_set)
    )

def reciprocal_rank(
        predicted_ids,
        expected_ids
):

    for rank,chunk_id in enumerate(
        predicted_ids,
        start = 1
    ):

        if chunk_id in expected_ids:
            return 1 / rank

    return 0.0

def create_stage_metrics():

    return {
        "total": 0,
        "top1_hits": 0,
        "hit3_sum": 0,
        "recall3_sum": 0.0,
        "rr_sum": 0.0
    }

def update_stage_metrics(
        metrics,
        predicted_ids,
        expected_ids
):

    metrics["total"] += 1

    metrics["top1_hits"] += (
        top1_hit(
            predicted_ids,
            expected_ids
        )
    )

    metrics["hit3_sum"] += (
        hit_at_k(
            predicted_ids,
            expected_ids,
            k = 3
        )
    )

    metrics["recall3_sum"] += (
        recall_at_k(
            predicted_ids,
            expected_ids,
            k = 3
        )
    )

    metrics["rr_sum"] += (
        reciprocal_rank(
            predicted_ids,
            expected_ids
        )
    )

def print_stage_result(
        stage_name,
        metrics
):

    total = metrics["total"]

    if total == 0:
        return

    top1 = (
        metrics["top1_hits"]
        / total
    )

    hit3 = (
        metrics["hit3_sum"]
        / total
    )

    recall3 = (
        metrics["recall3_sum"]
        / total
    )

    mrr = (
        metrics["rr_sum"]
        / total
    )

    print(f"\n======== {stage_name} =========")

    print(f"Top1命中率: {top1:.4f}")

    print(f"Hit@3: {hit3:.4f}")

    print(f"Recall@3: {recall3:.4f}")

    print(f"MRR: {mrr:.4f}")

def main():

    cases = load_eval_cases()

    metrics = {
        "chroma": create_stage_metrics(),
        "rrf": create_stage_metrics(),
        "reranker": create_stage_metrics()
    }

    reject_total = 0
    reject_correct = 0

    print("\n======== 开始消融评估 =========")

    for index, case in enumerate(cases, start = 1):

        question = case["question"]

        expected_ids = [
            str(chunk_id).strip()
            for chunk_id
            in case["expected_chunk_ids"]
        ]

        should_reject = (
            case["should_reject"]
        )

        stage_results = (
            hybrid_retriever.search(
                question,
                RETRIEVAL_TOP_K,
                return_stages = True
            )
        )

        chroma_ids = (
            extract_chunk_ids(
                stage_results["chroma"]
            )
        )

        rrf_ids = (
            extract_chunk_ids(
                stage_results["rrf"]
            )
        )

        reranker_ids = (
            extract_chunk_ids(
                stage_results["reranker"]
            )
        )

        print(f"\n======== 测试{index} ========")

        print(f"问题: {question}")

        print(f"预期: {expected_ids}")

        print(f"Chroma: {chroma_ids[:3]}")

        print(f"RRF: {rrf_ids[:3]}")

        print(f"Reranker: {reranker_ids[:3]}")

        # 知识库外问题
        if should_reject:

            reject_total += 1

            if len(chroma_ids) == 0:
                reject_correct += 1
                print(
                    "拒绝结果: 正确"
                )

            else:
                print(
                    "拒绝结果: 错误召回"
                )

            continue

        # 知识库内问题
        update_stage_metrics(
            metrics["chroma"],
            chroma_ids,
            expected_ids
        )

        update_stage_metrics(
            metrics["rrf"],
            rrf_ids,
            expected_ids
        )

        update_stage_metrics(
            metrics["reranker"],
            reranker_ids,
            expected_ids
        )

    print("\n\n======== 最终消融结果 ========")

    print_stage_result(
        "Chroma Only",
        metrics["chroma"]
    )

    print_stage_result(
        "Hybrid + RRF",
        metrics["rrf"]
    )

    print_stage_result(
        "Hybrid + RRF + Reranker",
        metrics["reranker"]
    )

    if reject_total > 0:

        reject_accuracy = (
            reject_correct
            / reject_total
        )

        print("\n======== 知识库外问题 =========")

        print(
            f"拒绝率:"
            f"{reject_accuracy:.4f}"
        )

if __name__ == "__main__":
    main()
