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
    ) as file:
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

def evaluate_hit(
        predicted_chunk_ids,
        expected_chunk_ids
):
    for chunk_id in predicted_chunk_ids:
        if chunk_id in expected_chunk_ids:
            return True

    return False

def reciprocal_rank(
        predicted_chunk_ids,
        expected_chunk_ids
):
    for rank, chunk_id in enumerate(
        predicted_chunk_ids,
        start = 1
    ):
        if chunk_id in expected_chunk_ids:
            return  1 / rank

    return 0.0

def main():
    cases = load_eval_cases()

    total_answerable = 0

    top1_hits = 0
    top3_hits = 0

    reciprocal_rank_sum = 0.0

    total_reject_case = 0
    correct_rejects = 0

    print(
        "\n=========== 开始检索评估 ===========\n"
    )

    for index, case in enumerate(
        cases,
        start = 1
    ):
        question = case["question"]

        expected_chunk_ids = [
            str(chunk_id).strip()
            for chunk_id
            in case["expected_chunk_ids"]
        ]

        should_reject = case[
            "should_reject"
        ]

        results = hybrid_retriever.search(
            question,
            RETRIEVAL_TOP_K
        )

        predicted_chunk_ids = (
            extract_chunk_ids(results)
        )

        print(
            f"\n============ 测试{index} =============\n"
        )
        print(
            f"问题:{question}"
        )
        print(
            f"预期文本块:"
            f"{expected_chunk_ids}"
        )
        print(
            f"实际文本块:"
            f"{predicted_chunk_ids}"
        )

        # 知识库外问题
        if should_reject:
            total_reject_case += 1

            if len(results) == 0:
                correct_rejects += 1

                print(
                    "结果: 正确拒绝"
                )

            else:
                print(
                    "结果: 错误召回"
                )

            continue

        # 知识库内问题
        total_answerable += 1

        top1_predicted = (
            predicted_chunk_ids[:1]
        )

        top3_predicted = (
            predicted_chunk_ids[:3]
        )

        if evaluate_hit(
            top1_predicted,
            expected_chunk_ids
        ):
            top1_hits += 1

        if evaluate_hit(
            top3_predicted,
            expected_chunk_ids
        ):
            top3_hits += 1

        rr = reciprocal_rank(
            predicted_chunk_ids,
            expected_chunk_ids
        )

        reciprocal_rank_sum += rr

        print(
            f"RR: {rr:.4f}"
        )

    print("\n======== 最终评估结果 =========")

    if total_answerable > 0:

        top1_accuracy = (
            top1_hits
            / total_answerable
        )

        top3_recall = (
            top3_hits
            / total_answerable
        )

        mrr = (
            reciprocal_rank_sum
            / total_answerable
        )

        print(
            f"Top1命中率:"
            f"{top1_accuracy:.4f}"
        )

        print(
            f"Recall@3:"
            f"{top3_recall:.4f}"
        )

        print(
            f"MRR:"
            f"{mrr:.4f}"
        )

    if total_reject_case > 0:
        reject_accuracy = (
            correct_rejects
            / total_reject_case
        )

        print(
            f"知识库外拒绝率:"
            f"{reject_accuracy:.4f}"
        )

if __name__ == "__main__":
    main()