# main.py
from experta import Rule, KnowledgeEngine, MATCH
from controller import converFact_to_string, response
from facts import knowledge_base, BookFact
import math

class LibraryExpertSystem(KnowledgeEngine):
    def __init__(self, knowledge_base):
        super().__init__()
        self.knowledge_base = knowledge_base
        self.inferred_books = []
        self.alternatives = []

    def normalize_kw(self, kw_set):
        """Normalize keywords for comparison"""
        if not kw_set:
            return set()
        return set([str(k).strip().lower() for k in kw_set])

    def normalize_text(self, text):
        """Normalize text fields for comparison"""
        if not text:
            return ""
        return str(text).strip().lower()

    def get_book_field(self, book, field_name, default=None):
        """Safely get field from book whether it's a BookFact object or dict"""
        if hasattr(book, field_name):
            return getattr(book, field_name, default)
        elif isinstance(book, dict) and field_name in book:
            return book[field_name]
        return default

    # --------------------------
    # Rule: Exact match - UPDATED WITH DEBUG
    # --------------------------
    @Rule(
        BookFact(
            category=MATCH.category,
            author=MATCH.author,
            target_audience=MATCH.target_audience,
            language=MATCH.language,
            book_type=MATCH.book_type,
            keywords=MATCH.keywords,
            rating=MATCH.rating
        ),
        salience=10
    )
    def exact_match(self, category, author, target_audience, language, book_type, keywords, rating):
        print(f"🚀 RULE FIRED: exact_match")
        print(f"📝 User input - category: '{category}', author: '{author}', audience: '{target_audience}'")
        print(f"📝 User input - language: '{language}', book_type: '{book_type}', rating: {rating}")
        print(f"📝 User keywords: {keywords}")
        
        keywords_norm = self.normalize_kw(keywords)
        print(f"🔧 Normalized keywords: {keywords_norm}")

        matched_books = []
        
        for i, book in enumerate(self.knowledge_base):
            # Get book fields safely
            book_title = self.get_book_field(book, "title", "Unknown")
            book_category = self.get_book_field(book, "category", "")
            book_author = self.get_book_field(book, "author", "")
            book_audience = self.get_book_field(book, "target_audience", "")
            book_language = self.get_book_field(book, "language", "")
            book_book_type = self.get_book_field(book, "book_type", "")
            book_keywords = self.get_book_field(book, "keywords", set())
            book_rating = self.get_book_field(book, "rating", 0.0)

            print(f"📚 Checking book {i+1}: '{book_title}'")
            print(f"   Book details - category: '{book_category}', author: '{book_author}'")

            # Flexible matching with debug
            category_match = (not category or 
                            self.normalize_text(book_category) == self.normalize_text(category))
            print(f"   Category match: {category_match} ('{book_category}' vs '{category}')")
            
            author_match = (not author or 
                          self.normalize_text(book_author) == self.normalize_text(author))
            print(f"   Author match: {author_match} ('{book_author}' vs '{author}')")
            
            audience_match = (not target_audience or 
                            self.normalize_text(book_audience) == self.normalize_text(target_audience))
            print(f"   Audience match: {audience_match} ('{book_audience}' vs '{target_audience}')")
            
            language_match = (not language or 
                            self.normalize_text(book_language) == self.normalize_text(language))
            print(f"   Language match: {language_match} ('{book_language}' vs '{language}')")
            
            type_match = (not book_type or 
                        self.normalize_text(book_book_type) == self.normalize_text(book_type))
            print(f"   Type match: {type_match} ('{book_book_type}' vs '{book_type}')")
            
            # Keyword matching - check if any keyword matches (more flexible)
            book_keywords_norm = self.normalize_kw(book_keywords)
            print(f"   Book keywords: {book_keywords_norm}")
            
            keyword_match = (not keywords_norm or 
                           any(kw in book_keywords_norm for kw in keywords_norm))
            print(f"   Keyword match: {keyword_match}")
            
            rating_match = (not rating or 
                          abs(float(book_rating) - float(rating)) <= 0.5)
            print(f"   Rating match: {rating_match} ({book_rating} vs {rating})")
            
            all_match = (category_match and author_match and audience_match and 
                        language_match and type_match and keyword_match and rating_match)
            print(f"   ALL MATCH: {all_match}")
            
            if all_match:
                matched_books.append(converFact_to_string(book))
                print(f"🎯 MATCH FOUND: {book_title}")

        self.inferred_books = matched_books
        print(f"📊 Total exact matches found: {len(self.inferred_books)}")

        if self.inferred_books:
            response.update({
                "response_messege": "Based on your preferences, these books match exactly what you're looking for:",
                "response_data": self.inferred_books
            })
            print(f"✅ Response updated with {len(self.inferred_books)} books")
        else:
            print("❌ No exact matches found, will try alternatives")

    # --------------------------
    # Rule: Suggest alternatives - UPDATED WITH DEBUG
    # --------------------------
    @Rule(
        BookFact(
            category=MATCH.category,
            author=MATCH.author,
            target_audience=MATCH.target_audience,
            language=MATCH.language,
            book_type=MATCH.book_type,
            keywords=MATCH.keywords,
            rating=MATCH.rating
        ),
        salience=7
    )
    def suggest_alternatives(self, category, author, target_audience, language, book_type, keywords, rating):
        print("🚀 RULE FIRED: suggest_alternatives")
        
        # Only run if no exact matches were found
        if self.inferred_books:
            print("📌 Exact matches exist, skipping alternatives")
            return

        keywords_norm = self.normalize_kw(keywords)
        self.alternatives = []

        print("🔄 Looking for alternative matches...")

        # Calculate relevance score for alternatives
        for book in self.knowledge_base:
            # Get book fields safely
            book_title = self.get_book_field(book, "title", "Unknown")
            book_category = self.get_book_field(book, "category", "")
            book_author = self.get_book_field(book, "author", "")
            book_audience = self.get_book_field(book, "target_audience", "")
            book_language = self.get_book_field(book, "language", "")
            book_book_type = self.get_book_field(book, "book_type", "")
            book_keywords = self.get_book_field(book, "keywords", set())
            book_rating = self.get_book_field(book, "rating", 0.0)

            relevance_score = 0
            book_keywords_norm = self.normalize_kw(book_keywords)

            # Keyword matching (partial matches)
            if keywords_norm:
                common_keywords = book_keywords_norm.intersection(keywords_norm)
                relevance_score += len(common_keywords) * 2
                print(f"   Keywords match for '{book_title}': {common_keywords} (+{len(common_keywords)*2})")

            # Field matching
            if category and self.normalize_text(book_category) == self.normalize_text(category):
                relevance_score += 3
                print(f"   Category match for '{book_title}': +3")
            if author and self.normalize_text(book_author) == self.normalize_text(author):
                relevance_score += 3
                print(f"   Author match for '{book_title}': +3")
            if target_audience and self.normalize_text(book_audience) == self.normalize_text(target_audience):
                relevance_score += 2
                print(f"   Audience match for '{book_title}': +2")
            if language and self.normalize_text(book_language) == self.normalize_text(language):
                relevance_score += 1
                print(f"   Language match for '{book_title}': +1")
            if book_type and self.normalize_text(book_book_type) == self.normalize_text(book_type):
                relevance_score += 2
                print(f"   Type match for '{book_title}': +2")
            if rating and abs(float(book_rating) - float(rating)) <= 0.5:
                relevance_score += 2
                print(f"   Rating match for '{book_title}': +2")

            # Only include books with some relevance
            if relevance_score > 0:
                score = min(100, relevance_score * 10)
                self.alternatives.append((converFact_to_string(book), score))
                print(f"🎯 Alternative found: '{book_title}' with score {score}")

        # Sort and limit alternatives
        self.alternatives.sort(key=lambda x: x[1], reverse=True)
        self.alternatives = self.alternatives[:5]

        if self.alternatives:
            response.update({
                "response_messege": "Here are some alternative recommendations based on your preferences:",
                "response_data": self.alternatives
            })
            print(f"✅ Alternatives updated with {len(self.alternatives)} books")
        else:
            response.update({
                "response_messege": "No books found matching your preferences. You can explore any book you like.",
                "response_data": []
            })
            print("❌ No alternatives found either")