from pathlib import Path

from sentence_transformers import CrossEncoder

class Reranker:

    def __init__(self):

            model_path = (
                Path(__file__).resolve().parent
                / "models"
                / "mmarco-reranker" 
            )

            self.model = CrossEncoder(
                str(model_path)
            )
            

    def rerank(
            self,
            question,
            documents_with_scores,
            top_k = 3
    ):
        if not documents_with_scores:
            return []

        pairs = [
            (
                question,
                doc.page_content
            )
            for doc, _ in documents_with_scores
        ]

        reranker_scores = self.model.predict(
            pairs
        )

        reranked_results = []

        for (
            doc,
            rrf_score
        ),reranker_score in zip(
            documents_with_scores,
            reranker_scores
        ):
            reranked_results.append(
                (
                    doc,
                    float(reranker_score),
                    float(rrf_score)
                )
            )

        reranked_results.sort(
            key = lambda x: x[1],
            reverse = True
        )

        return reranked_results[:top_k]