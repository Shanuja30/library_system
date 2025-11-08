# 📚 Expert Librarian System

Welcome to the **Expert Librarian System**! This platform helps you find the best books tailored to your preferences using an inference engine powered by the **experta** Python library.

---

## Features

### Personalized Book Recommendations
Get recommendations based on:

- **Category**
- **Author**
- **Topics (Keywords)**
- **Target Audience**
- **Book Type**
- **Language**

### Chatbot-Like Interface
A user-friendly chatbot guides you step-by-step to provide your preferences.it makes using streamlit.

### Inference Engine
Uses the **experta** library to create and apply rules for generating tailored recommendations.

---

## How It Works

### Step-by-Step Questions
The system asks the following questions to understand your requirements:

1. What type of category do you want?
2. Who is the author you prefer?
3. Tell me the topics related to the category you would like to refer to. It will help find the most suitable books.
4. How about the target audience, like teens or adults?
5. Which type of book do you hope for, like a novel or hardcover?
6. Which language do you prefer for the book?

### User Inputs
Based on your responses:

- Categories and authors are matched directly.
- Keywords are analyzed for relevance.

### Inference Engine
- The **experta** library manages the rules and facts to process user inputs and recommend books.
- Rules are designed to handle:
  - Exact matches
  - Partial matches (with relevance scores)
  - Suggestions for similar authors and topics
- Uses **forward chaining** to infer results based on facts provided by the user.

### Response Generation
The system provides:

- Books matching your exact preferences (if available)
- Alternatives with relevance scores
- Additional recommendations considering unspecified preferences

---

## Inference Engine Rules

- The rules are created using the **experta** library to handle exact matches, partial matches, and suggestions.
