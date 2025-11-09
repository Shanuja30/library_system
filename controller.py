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