# controller.py

def converFact_to_string(fact):
    """
    Convert BookFact or dict to standardized dictionary format
    """
    try:
        # Check if it's a dictionary first
        if isinstance(fact, dict):
            return {
                "title": fact.get("title", "Unknown Title"),
                "category": fact.get("category", "Unknown Category"),
                "author": fact.get("author", "Unknown Author"),
                "rating": float(fact.get("rating", 0.0)),
                "target_audience": fact.get("target_audience", "N/A"),
                "language": fact.get("language", "Unknown Language"),
                "book_type": fact.get("book_type", "N/A"),
                "keywords": list(fact.get("keywords", []))
            }
        
        # It's a BookFact object - use as_dict() method to get actual values
        # Experta Fact objects have an as_dict() method that returns the actual values
        if hasattr(fact, 'as_dict'):
            fact_dict = fact.as_dict()
            # Convert keywords set to list if needed
            keywords = fact_dict.get('keywords', set())
            if isinstance(keywords, set):
                keywords = list(keywords)
            elif not isinstance(keywords, list):
                keywords = list(keywords) if keywords else []
            
            return {
                "title": fact_dict.get("title", "Unknown Title"),
                "category": fact_dict.get("category", "Unknown Category"),
                "author": fact_dict.get("author", "Unknown Author"),
                "rating": float(fact_dict.get("rating", 0.0)),
                "target_audience": fact_dict.get("target_audience", "N/A"),
                "language": fact_dict.get("language", "Unknown Language"),
                "book_type": fact_dict.get("book_type", "N/A"),
                "keywords": keywords
            }
        else:
            # Fallback if as_dict() doesn't exist (shouldn't happen with experta)
            raise AttributeError("Fact object doesn't have as_dict() method")
            
    except Exception as e:
        print(f"Error in converFact_to_string: {e}")
        import traceback
        traceback.print_exc()
        # Return safe default
        return {
            "title": "Error Processing Book",
            "category": "Unknown",
            "author": "Unknown",
            "rating": 0.0,
            "target_audience": "N/A",
            "language": "Unknown",
            "book_type": "N/A",
            "keywords": []
        }


response = {
    "response_messege": "",
    "response_data": []
}

# ------------------------------
# Lightweight ML-style similarity
# ------------------------------
import math
import re
from collections import Counter, defaultdict

_ML_INDEX_BUILT = False
_IDF: dict = {}
_VOCAB: set = set()

def _tokenize(text: str) -> list:
    if not text:
        return []
    return re.findall(r"[a-z0-9]+", str(text).lower())

def _book_to_text(book: dict) -> str:
    # Concatenate book metadata fields for similarity
    fields = [
        book.get("title", ""),
        book.get("author", ""),
        book.get("category", ""),
        " ".join(book.get("keywords", [])) if isinstance(book.get("keywords", []), (list, set)) else str(book.get("keywords", "")),
        book.get("target_audience", ""),
        book.get("language", ""),
        book.get("book_type", ""),
    ]
    return " ".join([str(f) for f in fields if f])

def ensure_ml_index(knowledge_base) -> None:
    """Build a simple IDF index over the corpus (only once per process)."""
    global _ML_INDEX_BUILT, _IDF, _VOCAB
    if _ML_INDEX_BUILT:
        return
    docs = []
    for fact in knowledge_base:
        book = converFact_to_string(fact)
        text = _book_to_text(book)
        tokens = set(_tokenize(text))
        docs.append(tokens)
        _VOCAB.update(tokens)
    # Compute IDF
    N = max(1, len(docs))
    df = defaultdict(int)
    for tokens in docs:
        for t in tokens:
            df[t] += 1
    _IDF = {t: math.log((N + 1) / (df_t + 1)) + 1.0 for t, df_t in df.items()}
    _ML_INDEX_BUILT = True

def _tfidf_vector(tokens: list) -> dict:
    counts = Counter(tokens)
    vec = {}
    for t, c in counts.items():
        if t in _IDF:
            vec[t] = (1.0 + math.log(c)) * _IDF[t]
    return vec

def _cosine_sim(vec_a: dict, vec_b: dict) -> float:
    if not vec_a or not vec_b:
        return 0.0
    # dot
    dot = 0.0
    for t, wa in vec_a.items():
        wb = vec_b.get(t)
        if wb:
            dot += wa * wb
    # norms
    na = math.sqrt(sum(w * w for w in vec_a.values()))
    nb = math.sqrt(sum(w * w for w in vec_b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)

def ml_similarity_for_book(book: dict, user_params: dict) -> float:
    """
    Compute cosine similarity between user preferences text and book metadata text.
    Returns a float in [0,1].
    """
    # Build user text
    user_text_parts = [
        user_params.get("category") or "",
        user_params.get("author") or "",
        " ".join(user_params.get("keywords", [])) if isinstance(user_params.get("keywords", []), (list, set)) else str(user_params.get("keywords", "")),
        user_params.get("target_audience") or "",
        user_params.get("language") or "",
        user_params.get("book_type") or "",
    ]
    user_text = " ".join([str(p) for p in user_text_parts if p])
    user_tokens = _tokenize(user_text)
    book_tokens = _tokenize(_book_to_text(book))
    user_vec = _tfidf_vector(user_tokens)
    book_vec = _tfidf_vector(book_tokens)
    return _cosine_sim(user_vec, book_vec)

# ------------------------------
# Explanations
# ------------------------------
def generate_recommendation_explanation(book: dict, user_params: dict) -> str:
    """
    Create a short human-readable explanation based on matched fields and rating proximity.
    """
    reasons = []
    # Field matches
    if user_params.get("category") and str(book.get("category", "")).lower() == str(user_params.get("category", "")).lower():
        reasons.append("matches your category")
    if user_params.get("author") and str(book.get("author", "")).lower() == str(user_params.get("author", "")).lower():
        reasons.append("same author")
    if user_params.get("language") and str(book.get("language", "")).lower() == str(user_params.get("language", "")).lower():
        reasons.append("preferred language")
    if user_params.get("book_type") and str(book.get("book_type", "")).lower() == str(user_params.get("book_type", "")).lower():
        reasons.append("requested book type")
    if user_params.get("target_audience") and str(book.get("target_audience", "")).lower() == str(user_params.get("target_audience", "")).lower():
        reasons.append("target audience match")
    # Keywords overlap
    try:
        user_kw = set([str(k).lower() for k in (user_params.get("keywords") or [])])
        book_kw = set([str(k).lower() for k in (book.get("keywords") or [])])
        if user_kw and book_kw:
            overlap = user_kw.intersection(book_kw)
            if overlap:
                reasons.append(f"keyword overlap: {', '.join(sorted(overlap))}")
    except Exception:
        pass
    # Rating proximity
    try:
        desired = float(user_params.get("rating")) if user_params.get("rating") is not None else None
        br = float(book.get("rating")) if book.get("rating") is not None else None
        if desired is not None and br is not None:
            diff = abs(desired - br)
            if diff <= 0.3:
                reasons.append("rating very close to your preference")
            elif diff <= 0.5:
                reasons.append("rating close to your preference")
    except Exception:
        pass
    if not reasons:
        return "overall content similarity to your preferences"
    return ", ".join(reasons)

def get_book(book: dict):
    try:
        rating = book.get('rating', 0.0)
        rating_display = f"{rating} ⭐" if rating else "Not rated"
        
        return f"""
Title: {book.get('title', 'Unknown Title')}
Author: {book.get('author', 'Unknown Author')}
Category: {book.get('category', 'Unknown Category')}
Rating: {rating_display}
Target Audience: {book.get('target_audience', 'N/A')}
Language: {book.get('language', 'Unknown Language')}
Book Type: {book.get('book_type', 'N/A')}
Keywords: {', '.join(book.get('keywords', []))}
"""
    except Exception as e:
        return f"Error formatting book: {e}"
    
# ... your existing controller.py code ...

def get_book(book: dict):
    try:
        rating = book.get('rating', 0.0)
        rating_display = f"{rating} ⭐" if rating else "Not rated"
        
        return f"""
Title: {book.get('title', 'Unknown Title')}
Author: {book.get('author', 'Unknown Author')}
Category: {book.get('category', 'Unknown Category')}
Rating: {rating_display}
Target Audience: {book.get('target_audience', 'N/A')}
Language: {book.get('language', 'Unknown Language')}
Book Type: {book.get('book_type', 'N/A')}
Keywords: {', '.join(book.get('keywords', []))}
"""
    except Exception as e:
        return f"Error formatting book: {e}"

# ⭐⭐⭐ ADD THIS NEW FUNCTION RIGHT HERE ⭐⭐⭐
def generate_recommendation_explanation(book, user_params):
    """
    Generate an explanation for why a book is being recommended
    based on user preferences
    """
    reasons = []
    
    # Extract book data safely
    if hasattr(book, 'as_dict'):
        book_dict = book.as_dict()
    else:
        book_dict = book
    
    # Get book fields
    book_title = book_dict.get('title', 'Unknown Title')
    book_category = book_dict.get('category', '')
    book_author = book_dict.get('author', '')
    book_keywords = book_dict.get('keywords', set())
    book_target = book_dict.get('target_audience', '')
    book_language = book_dict.get('language', '')
    book_type = book_dict.get('book_type', '')
    
    # Get user preferences
    user_cat = user_params.get('category', '').lower() if user_params.get('category') else ''
    user_author = user_params.get('author', '').lower() if user_params.get('author') else ''
    user_keywords = user_params.get('keywords', set())
    user_target = user_params.get('target_audience', '').lower() if user_params.get('target_audience') else ''
    user_language = user_params.get('language', '').lower() if user_params.get('language') else ''
    user_type = user_params.get('book_type', '').lower() if user_params.get('book_type') else ''
    
    # Build explanation based on matches
    if user_cat and book_category.lower() == user_cat:
        reasons.append(f"it matches your preferred **{book_category}** category")
    
    if user_author and book_author.lower() == user_author:
        reasons.append(f"it's written by your preferred author **{book_author}**")
    
    # Keyword matches
    if user_keywords and book_keywords:
        book_keywords_lower = {str(k).lower() for k in book_keywords}
        user_keywords_lower = {str(k).lower() for k in user_keywords}
        common_keywords = book_keywords_lower.intersection(user_keywords_lower)
        if common_keywords:
            keyword_list = ", ".join([f"**{kw}**" for kw in common_keywords])
            reasons.append(f"it covers topics you're interested in: {keyword_list}")
    
    if user_target and book_target.lower() == user_target:
        reasons.append(f"it's perfect for **{book_target}** audience")
    
    if user_language and book_language.lower() == user_language:
        reasons.append(f"it's available in your preferred **{book_language}** language")
    
    if user_type and book_type.lower() == user_type:
        reasons.append(f"it's the **{book_type}** format you wanted")
    
    # If no specific reasons found, provide a general explanation
    if not reasons:
        return f"**{book_title}** is recommended based on your overall preferences."
    
    # Combine reasons into a natural sentence
    if len(reasons) == 1:
        explanation = f"**{book_title}** is recommended because {reasons[0]}."
    elif len(reasons) == 2:
        explanation = f"**{book_title}** is recommended because {reasons[0]} and {reasons[1]}."
    else:
        explanation = f"**{book_title}** is recommended because {', '.join(reasons[:-1])}, and {reasons[-1]}."
    
    return explanation