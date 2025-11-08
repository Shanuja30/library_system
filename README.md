# Library Expert System

An expert system for book recommendations using forward and backward chaining.

## Setup

1. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Option 1: Streamlit Web Interface (Recommended)

Run the interactive web interface:
```bash
streamlit run st.py
```

This will open a web browser with the interactive interface where you can:
- Answer questions about your book preferences
- Get personalized book recommendations
- See confidence scores for recommendations

### Option 2: Command Line Interface

Run the command-line version:
```bash
python main.py
```

This will run with the default test parameters defined in `main.py`.

To customize the search, edit the `user_params` in `main.py` (around line 192):

```python
user_params = BookFact(
    category="Technology",
    author="Andrew Ng",
    keywords={"AI", "machine learning"},
    target_audience="Adults",
    language="English",
    book_type="Paperback"
)
```

## Project Structure

- `st.py` - Streamlit web interface
- `main.py` - Command-line interface and expert system engine
- `facts.py` - Knowledge base with book facts
- `controller.py` - Utility functions for data conversion

## Features

- Forward chaining for book recommendations
- Backward chaining to find book categories by title
- Keyword matching
- Relevance scoring
- Multiple recommendation strategies

