import streamlit as st
from controller import converFact_to_string, response, get_book
from facts import knowledge_base, BookFact
from main import LibraryExpertSystem


# Streamlit app initialization
st.set_page_config(page_title="Library Expert System", layout="centered")

# MOVE THIS FUNCTION TO THE TOP - RIGHT AFTER IMPORTS
def reset_application():
    """Reset the entire application state"""
    st.session_state.step = 0
    st.session_state.user_params = {
        "category": None,
        "author": None,
        "keywords": set(),
        "target_audience": None,
        "book_type": None,
        "language": None,
        "rating": 4.0,
    }
    st.session_state.messages = [{"role": "assistant", "content": "How can I assist you with your book preferences today?"}]
    # Clear the response
    response.update({
        "response_messege": "",
        "response_data": []
    })
    st.rerun()

def display_book_details(book: dict, index: int):
    """Display book details in a formatted way"""
    # Create columns for better layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write(f"**Title**: {book.get('title', 'Unknown Title')}")
        st.write(f"**Author**: {book.get('author', 'Unknown Author')}")
        st.write(f"**Category**: {book.get('category', 'Unknown Category')}")
        
        # Show rating if available
        rating = book.get('rating')
        if rating:
            st.write(f"**Rating**: {rating} ⭐")
        
        # Show additional details in expander
        with st.expander("More details"):
            st.write(f"**Target Audience**: {book.get('target_audience', 'N/A')}")
            st.write(f"**Language**: {book.get('language', 'Unknown Language')}")
            st.write(f"**Book Type**: {book.get('book_type', 'N/A')}")
            keywords = book.get('keywords', [])
            if keywords:
                # Handle both list and set types
                if isinstance(keywords, (list, set)):
                    keywords_str = ', '.join(str(k) for k in keywords)
                else:
                    keywords_str = str(keywords)
                st.write(f"**Keywords**: {keywords_str}")
    
    with col2:
        # You can add book cover placeholder or other visual elements here
        st.markdown("📖")

# Chatbot interface
st.title("📚 Expert Librarian System")

questions = [
    "What type of category do you want?",
    "Who is the author you prefer?",
    "Tell me the topics related to the category you would like to refer. It will be helpful to find the most suitable books.",
    "How about the target audience, like teens or adults?",
    "Which type of book do you hope for, like a novel or hardcover?",
    "Which language do you prefer for the book?",
]

# Initialize session state
if "user_params" not in st.session_state:
    st.session_state.user_params = {
        "category": None,
        "author": None,
        "keywords": set(),
        "target_audience": None,
        "book_type": None,
        "language": None,
        "rating": 4.0,  # ADDED: Default rating
    }

if "step" not in st.session_state:
    st.session_state.step = 0

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I assist you with your book preferences today?"}]

# Display chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User input handling
if st.session_state.step < len(questions):
    with st.form(key=f"form_{st.session_state.step}"):
        user_input = st.text_input(questions[st.session_state.step])
        submit = st.form_submit_button("Next")
        if submit:
            key = list(st.session_state.user_params.keys())[st.session_state.step]
            
            # Normalize keywords and text inputs
            if key == "keywords":
                st.session_state.user_params[key] = set([k.strip().lower() for k in user_input.split(",")]) if user_input else set()
            else:
                st.session_state.user_params[key] = user_input.strip() if user_input else None

            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.step += 1
            st.rerun()

# Run expert system after collecting inputs
if st.session_state.step == len(questions):
    st.success("Thank you for providing your preferences! Let's find the best recommendations for you.")
    
   

    # Convert inputs to BookFact
    user_params_fact = BookFact(
        category=st.session_state.user_params.get("category"),
        author=st.session_state.user_params.get("author"),
        keywords=st.session_state.user_params.get("keywords", set()),
        target_audience=st.session_state.user_params.get("target_audience"),
        language=st.session_state.user_params.get("language"),
        book_type=st.session_state.user_params.get("book_type"),
        
    )

# In st.py, update the error handling section:

    # Run expert system
    try:
        # Clear previous response first
        response.update({
            "response_messege": "",
            "response_data": []
        })
        
        engine = LibraryExpertSystem(knowledge_base)
        engine.reset()
        engine.declare(user_params_fact)
        engine.run()

        # Fallback: If no recommendations were found, provide some anyway
        response_data = response.get("response_data", [])
        if not response_data or len(response_data) == 0:
            # Manually search for recommendations
            from controller import converFact_to_string
            recommendations = []
            user_cat = st.session_state.user_params.get("category", "").strip().lower() if st.session_state.user_params.get("category") else ""
            user_author = st.session_state.user_params.get("author", "").strip().lower() if st.session_state.user_params.get("author") else ""
            user_keywords = st.session_state.user_params.get("keywords", set())
            user_target = st.session_state.user_params.get("target_audience", "").strip().lower() if st.session_state.user_params.get("target_audience") else ""
            user_lang = st.session_state.user_params.get("language", "").strip().lower() if st.session_state.user_params.get("language") else ""
            user_type = st.session_state.user_params.get("book_type", "").strip().lower() if st.session_state.user_params.get("book_type") else ""
            
            for book in knowledge_base:
                # Use as_dict() to get actual values from BookFact objects
                try:
                    book_dict = book.as_dict() if hasattr(book, 'as_dict') else book
                except Exception as e:
                    continue
                
                # Safely extract values
                book_cat = str(book_dict.get('category', '')).strip().lower() if book_dict.get('category') else ''
                book_author = str(book_dict.get('author', '')).strip().lower() if book_dict.get('author') else ''
                book_keywords = book_dict.get('keywords', set())
                book_target = str(book_dict.get('target_audience', '')).strip().lower() if book_dict.get('target_audience') else ''
                book_lang = str(book_dict.get('language', '')).strip().lower() if book_dict.get('language') else ''
                book_type = str(book_dict.get('book_type', '')).strip().lower() if book_dict.get('book_type') else ''
                
                score = 0
                # Category match
                if user_cat and book_cat == user_cat:
                    score += 10
                # Author match
                if user_author and book_author == user_author:
                    score += 10
                # Keywords match (case-insensitive)
                if user_keywords and book_keywords:
                    try:
                        # Convert both to lowercase for case-insensitive matching
                        if isinstance(book_keywords, set):
                            book_keywords_lower = {str(k).strip().lower() for k in book_keywords if k}
                        elif isinstance(book_keywords, list):
                            book_keywords_lower = {str(k).strip().lower() for k in book_keywords if k}
                        else:
                            book_keywords_lower = set()
                        
                        if isinstance(user_keywords, set):
                            user_keywords_lower = {str(k).strip().lower() for k in user_keywords if k}
                        elif isinstance(user_keywords, list):
                            user_keywords_lower = {str(k).strip().lower() for k in user_keywords if k}
                        else:
                            user_keywords_lower = set()
                        
                        if book_keywords_lower and user_keywords_lower:
                            keyword_matches = len(book_keywords_lower.intersection(user_keywords_lower))
                            score += keyword_matches * 5
                    except Exception:
                        pass  # Skip keyword matching if there's an error
                # Target audience match
                if user_target and book_target == user_target:
                    score += 5
                # Language match
                if user_lang and book_lang == user_lang:
                    score += 3
                # Book type match
                if user_type and book_type == user_type:
                    score += 2
                
                if score > 0:
                    recommendations.append((converFact_to_string(book), score))
            
            recommendations.sort(key=lambda x: x[1], reverse=True)
            if recommendations:
                response.update({
                    "response_messege": f"Here are {len(recommendations)} books that match your preferences:",
                    "response_data": recommendations[:10]  # Top 10 recommendations
                })
            else:
                # If still no recommendations, show some general ones based on category/author
                # Try to find at least category or author matches
                partial_recs = []
                for book in knowledge_base:
                    try:
                        book_dict = book.as_dict() if hasattr(book, 'as_dict') else book
                        book_cat = book_dict.get('category', '').lower() if book_dict.get('category') else ''
                        book_author = book_dict.get('author', '').lower() if book_dict.get('author') else ''
                        
                        if (user_cat and book_cat == user_cat) or (user_author and book_author == user_author):
                            partial_recs.append(converFact_to_string(book))
                    except:
                        continue
                
                if partial_recs:
                    response.update({
                        "response_messege": "Here are some books related to your search:",
                        "response_data": partial_recs[:10]
                    })
                else:
                    # Last resort: show general books
                    general_recs = [converFact_to_string(book) for book in knowledge_base[:5]]
                    response.update({
                        "response_messege": "Here are some popular books from our collection:",
                        "response_data": general_recs
                    })
        
        # Display recommendations
        st.write("### 📚 Recommendations:")
        
        if response and response.get("response_messege"):
            st.info(response["response_messege"])
        
        if response and response.get("response_data"):
            response_data = response["response_data"]
            st.write(f"Found {len(response_data)} recommendation(s)")
            
            for i, item in enumerate(response_data, start=1):
                st.write("---")
                st.write(f"### **{i}. Book Recommendation**")
                
                if isinstance(item, dict):
                    # Direct dictionary format (exact matches)
                    display_book_details(item, i)
                
                elif isinstance(item, tuple) and len(item) == 2:
                    # Alternative format with score
                    book_ref, score = item
                    st.write(f"**Confidence Level**: {score}%")
                    
                    if isinstance(book_ref, dict):
                        display_book_details(book_ref, i)
                    else:
                        # Use the get_book function for other formats
                        st.write(get_book(book_ref))
                
                else:
                    # Fallback for any other format
                    st.write("Book data:", item)
        
        else:
            st.warning("No recommendations found. Try broadening your search criteria.")
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("### 🔧 Technical Details (for debugging):")
        st.code(f"Error type: {type(e).__name__}\nError message: {str(e)}")
        st.write("Please try again with different preferences.")

# Reset button
    if st.button("Start Over"):
        reset_application()


# Add some helpful information in sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This Expert Librarian System uses AI to find books matching your preferences.
    
    **How it works:**
    1. Answer questions about your preferences
    2. Our system searches for matches
    3. Get personalized recommendations
    
    **Available categories include:**
    - Fiction, Technology, Science
    - Business, Self-help, Biography  
    - Fantasy, Mystery, and more!
    """)
    
    st.header("📊 Statistics")
    st.metric("Books in Database", len(knowledge_base))
    
    # Show some quick stats
    categories = len(set(book.category for book in knowledge_base))
    st.metric("Available Categories", categories)