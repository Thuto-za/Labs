import os
import json
import random
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAI
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Initialize Gemini LLM model (Google Generative AI)
api_key = os.getenv("GOOGLE_API_KEY")  # Ensure you set this environment variable
llm = GoogleGenerativeAI(model="gemini-pro", api_key="")

# List of emojis to add some liveliness to responses
emojis = ['😄', '😊', '🤖', '📄', '✨', '💬', '📚', '👍', '🤔', '✅', '👀', '🤓']

def get_random_emoji():
    """Returns a random emoji from the list."""
    return random.choice(emojis)

# Define the Mwanga chatbot class
class MwangaChatbot:
    def __init__(self, pdf_file):
        """Initialize the chatbot with a PDF file."""
        self.pdf_text = self._load_pdf(pdf_file)
    
    def _load_pdf(self, pdf_file):
        """Extract text from the provided PDF file using PyPDFLoader."""
        try:
            # Use PyPDFLoader to load and split the PDF into pages
            loader = PyPDFLoader(pdf_file)
            pages = loader.load_and_split()
            all_page_content = "\n\n".join(str(page) for page in pages)
            return all_page_content
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return ""

    def query_pdf(self, user_query):
        """Use Gemini LLM to answer the query based on the PDF content."""
        if not self.pdf_text:
            return f"Oops! It looks like I can't find the PDF content 😕. Let's make sure it's properly loaded."

        # Define the prompt for the LLM based on user query and PDF content
        prompt = f"""
        You are Mwanga, a helpful assistant for product inquiries. The user is asking about a product: '{user_query}'.
        Use the following PDF content, which contains a catalog of portable energy storage products powered by batteries, to answer the query:
        
        PDF Content (First 2000 characters for context):
        {self.pdf_text[:2000]}... (truncated)
        
        Respond with helpful information about the product based on the PDF content.
        """
        
        try:
            # Call the Google Generative AI (Gemini LLM) to process the query
            response = llm.invoke(prompt)
            return self._format_response(response.strip())
        except Exception as e:
            return f"Oops, something went wrong when I tried to look for an answer 🤖 {get_random_emoji()}. Here's the error: {e}"

    def _format_response(self, response):
        """Format the chatbot's response to make it more friendly and engaging."""
        # Add some human-like expressions and emojis to the response
        human_phrases = [
            "Here's what I found for you 😊:",
            "Ah, I think I have the perfect answer for that! 👀",
            "Let me break it down for you 📚:",
            "Got it! Here's what I learned 🧠:",
            "Sure thing! Let me explain ✨:"
        ]
        # Randomly pick a human-like introduction phrase
        intro = random.choice(human_phrases)
        return f"{intro} {get_random_emoji()}\n\n{response}"

def main():
    """Main function to run the chatbot."""
    # Define the path to the PDF file
    pdf_path = input("Enter the path to the PDF file: ")
    
    if not os.path.exists(pdf_path):
        print("Hmm, I can't seem to find that file. Can you double-check the path? 🤔")
        return

    # Initialize the Mwanga chatbot
    chatbot = MwangaChatbot(pdf_path)
    
    # Simulate a chat loop
    print("Mwanga Chatbot is ready to chat! Ask me anything about the portable energy storage products 📄. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye! 👋 Take care!")
            break
        
        # Get the chatbot response based on the user query
        response = chatbot.query_pdf(user_input)
        print(f"Mwanga: {response}")

if __name__ == "__main__":
    main()
