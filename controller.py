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