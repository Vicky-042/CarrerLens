from sentence_transformers import SentenceTransformer, util

# Load once — stays in memory for the whole session
# This is why the first scan takes 10-15 seconds longer
# Every scan after that is fast
MODEL = SentenceTransformer("all-MiniLM-L6-v2")

def bert_similarity_score(resume_text: str, jd_text: str) -> dict:
    """
    Feynman: BERT reads the full meaning of both documents.
    'Built ML models' and 'machine learning experience' 
    score HIGH here even though they share no exact words.
    TF-IDF would give them near zero — BERT catches this.
    """
    resume_embedding = MODEL.encode(resume_text, convert_to_tensor=True)
    jd_embedding     = MODEL.encode(jd_text,     convert_to_tensor=True)

    similarity = util.cos_sim(resume_embedding, jd_embedding).item()
    
    # Clamp to 0-100 range
    score = max(0.0, min(100.0, similarity * 100))

    return {
        "bert_score": round(score, 1)
    }

def hybrid_score(tfidf_score: float, bert_score: float) -> float:
    """
    Final score = 40% TF-IDF + 60% BERT
    TF-IDF catches exact keyword matches (what ATS looks for)
    BERT catches semantic meaning (what humans look for)
    Together they give a more honest picture.
    """
    return round((0.4 * tfidf_score) + (0.6 * bert_score), 1)