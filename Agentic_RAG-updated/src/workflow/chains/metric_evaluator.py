# import numpy as np
# from rouge_score import rouge_scorer
# from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
# from nltk.translate.meteor_score import meteor_score
# from bert_score import score as bert_score
# from sklearn.metrics.pairwise import cosine_similarity
# from sentence_transformers import SentenceTransformer


# embedder = SentenceTransformer("all-MiniLM-L6-v2")
# smoothie = SmoothingFunction().method4

# def normalize(text: str) -> str:
#     return text.lower().strip()


# def compute_all_metrics(pred: str, gt: str):
#     pred_n = normalize(pred)
#     gt_n = normalize(gt)

#     # ROUGE
#     scorer = rouge_scorer.RougeScorer(['rouge1','rouge2','rougeL'], use_stemmer=True)
#     rouge = scorer.score(gt_n, pred_n)
#     r1 = rouge["rouge1"].fmeasure
#     r2 = rouge["rouge2"].fmeasure
#     rL = rouge["rougeL"].fmeasure

#     # BLEU
#     bleu = sentence_bleu([gt_n.split()], pred_n.split(), smoothing_function=smoothie)

#     # METEOR
#     meteor = meteor_score([gt_n.split()], pred_n.split())

#     # BERTScore
#     P, R, F1 = bert_score([pred_n], [gt_n], lang='en', rescale_with_baseline=True)
#     bert_f1 = float(F1[0])

#     # Cosine similarity
#     emb_pred = embedder.encode([pred_n])[0]
#     emb_gt = embedder.encode([gt_n])[0]
#     cos_sim = float(cosine_similarity([emb_pred], [emb_gt])[0][0])

#     # Faithfulness & coverage
#     pred_tokens = set(pred_n.split())
#     gt_tokens = set(gt_n.split())
#     common = pred_tokens & gt_tokens

#     faithfulness = len(common) / len(gt_tokens) if gt_tokens else 0
#     terminology_precision = len(common) / len(pred_tokens) if pred_tokens else 0
#     coverage = len(common) / len(gt_tokens) if gt_tokens else 0

#     return {
#         "rouge1": r1,
#         "rouge2": r2,
#         "rougeL": rL,
#         "bleu": bleu,
#         "meteor": meteor,
#         "bert_f1": bert_f1,
#         "cosine_sim": cos_sim,
#         "faithfulness": faithfulness,
#         "terminology_precision": terminology_precision,
#         "coverage": coverage
#     }


# def compute_final_score(metrics: dict) -> float:
#     # Weighted composite score
#     return (
#         0.25 * metrics["bert_f1"] +
#         0.20 * metrics["rougeL"] +
#         0.15 * metrics["rouge2"] +
#         0.10 * metrics["bleu"] +
#         0.10 * metrics["meteor"] +
#         0.10 * metrics["cosine_sim"]
#     )


# def evaluate_answers(gemini_ans, perplexity_ans, ground_truth):
#     m_gemini = compute_all_metrics(gemini_ans, ground_truth)
#     m_perp = compute_all_metrics(perplexity_ans, ground_truth)

#     score_gemini = compute_final_score(m_gemini)
#     score_perp = compute_final_score(m_perp)

#     winner = "gemini" if score_gemini >= score_perp else "perplexity"

#     return {
#         "winner": winner,
#         "gemini_score": score_gemini,
#         "perplexity_score": score_perp,
#         "gemini_metrics": m_gemini,
#         "perplexity_metrics": m_perp
#     }

#################Update to evaluate with context#################################
# src/workflow/chains/metric_evaluator.py
# src/workflow/chains/metric_evaluator.py
import numpy as np
from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.translate.meteor_score import meteor_score
from bert_score import score as bert_score
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("all-MiniLM-L6-v2")
smoothie = SmoothingFunction().method4

def normalize(text: str) -> str:
    return text.lower().strip()

def compute_context_metrics(pred: str, context: str):
    """Compute metrics comparing answer to retrieved context."""
    pred_n = normalize(pred)
    context_n = normalize(context)
    
    # Split context into sentences/chunks for better comparison
    context_chunks = [chunk.strip() for chunk in context_n.split('.') if chunk.strip()]
    
    # ROUGE against context
    scorer = rouge_scorer.RougeScorer(['rouge1','rouge2','rougeL'], use_stemmer=True)
    rouge_scores = []
    for chunk in context_chunks[:5]:  # Compare with top 5 context chunks
        if len(chunk) > 20:  # Only meaningful chunks
            rouge = scorer.score(chunk, pred_n)
            rouge_scores.append(rouge)
    
    # Average ROUGE scores
    if rouge_scores:
        r1 = float(np.mean([s["rouge1"].fmeasure for s in rouge_scores]))
        r2 = float(np.mean([s["rouge2"].fmeasure for s in rouge_scores]))
        rL = float(np.mean([s["rougeL"].fmeasure for s in rouge_scores]))
    else:
        r1 = r2 = rL = 0.0

    # BLEU - use context chunks as references
    if context_chunks:
        references = [chunk.split() for chunk in context_chunks if len(chunk.split()) > 3]
        if references:
            bleu = float(sentence_bleu(references, pred_n.split(), smoothing_function=smoothie))
        else:
            bleu = 0.0
    else:
        bleu = 0.0

    # METEOR
    if context_chunks:
        meteor_scores = []
        for chunk in context_chunks[:3]:
            if len(chunk.split()) > 3:
                try:
                    meteor = float(meteor_score([chunk.split()], pred_n.split()))
                    meteor_scores.append(meteor)
                except:
                    continue
        meteor = float(np.mean(meteor_scores)) if meteor_scores else 0.0
    else:
        meteor = 0.0

    # BERTScore against context
    if context_n.strip():
        P, R, F1 = bert_score([pred_n], [context_n], lang='en', rescale_with_baseline=True)
        bert_f1 = float(F1[0])
    else:
        bert_f1 = 0.0

    # Cosine similarity with context
    emb_pred = embedder.encode([pred_n])[0]
    emb_ctx = embedder.encode([context_n])[0]
    cos_sim = float(cosine_similarity([emb_pred], [emb_ctx])[0][0])

    # Factual consistency metrics
    pred_tokens = set(pred_n.split())
    context_tokens = set(context_n.split())
    common = pred_tokens & context_tokens

    # Faithfulness: how much of answer comes from context
    faithfulness = float(len(common) / len(pred_tokens)) if pred_tokens else 0.0
    
    # Context utilization: how much context is used
    context_utilization = float(len(common) / len(context_tokens)) if context_tokens else 0.0
    
    # Novel terms: terms in answer not in context (potential hallucination)
    novel_terms = float(len(pred_tokens - context_tokens) / len(pred_tokens)) if pred_tokens else 0.0

    return {
        "rouge1": r1,
        "rouge2": r2,
        "rougeL": rL,
        "bleu": bleu,
        "meteor": meteor,
        "bert_f1": bert_f1,
        "cosine_sim": cos_sim,
        "faithfulness": faithfulness,
        "context_utilization": context_utilization,
        "novel_terms_ratio": novel_terms
    }

def compute_context_score(metrics: dict) -> float:
    """Weighted score favoring faithfulness and context utilization."""
    return float(
        0.30 * metrics["faithfulness"] +      # Most important: grounded in context
        0.25 * metrics["bert_f1"] +           # Semantic similarity to context
        0.15 * metrics["cosine_sim"] +        # Embedding similarity
        0.10 * metrics["rougeL"] +            # Overlap with context
        0.10 * metrics["context_utilization"] + # How much context is used
        0.10 * (1 - metrics["novel_terms_ratio"])  # Penalize novel terms
    )

def evaluate_answers_with_context(gemini_ans, perplexity_ans, context):
    """Evaluate both answers against the retrieved context."""
    m_gemini = compute_context_metrics(gemini_ans, context)
    m_perp = compute_context_metrics(perplexity_ans, context)

    score_gemini = compute_context_score(m_gemini)
    score_perp = compute_context_score(m_perp)

    winner = "gemini" if score_gemini >= score_perp else "perplexity"

    # Convert all numpy types to Python native types
    result = {
        "winner": winner,
        "gemini_score": float(score_gemini),
        "perplexity_score": float(score_perp),
        "gemini_metrics": {k: float(v) for k, v in m_gemini.items()},
        "perplexity_metrics": {k: float(v) for k, v in m_perp.items()},
        "evaluation_note": "Evaluated against retrieved context for factual consistency"
    }
    
    return result