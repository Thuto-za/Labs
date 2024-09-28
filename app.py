import os
import json
import random
from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAI
from dotenv import load_dotenv

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'

socketio = SocketIO(app)

# Load environment variables
load_dotenv()

# Initialize Google Generative AI
api_key = os.getenv("GOOGLE_API_KEY")
llm = GoogleGenerativeAI(model="gemini-pro", api_key=api_key)

# List of emojis for fun responses
emojis = ['😄', '😊', '🤖', '📄', '✨', '💬', '📚', '👍', '🤔', '✅', '👀', '🤓']

def get_random_emoji():
    """Returns a random emoji from the list."""
    return random.choice(emojis)

class MwangaChatbot:
    def __init__(self, pdf_file):
        """Initialize chatbot with a PDF file."""
        self.pdf_text = self._load_pdf(pdf_file)

    def _load_pdf(self, pdf_file):
        """Extract text from PDF using PyPDFLoader."""
        try:
            loader = PyPDFLoader(pdf_file)
            pages = loader.load_and_split()
            return "\n\n".join(str(page) for page in pages)
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return ""

    def query_pdf(self, user_query):
        """Try to answer queries based on PDF content, fallback to Gemini LLM if necessary."""
        print("Calling action")
        if not self.pdf_text:
            return "Oops! Couldn't load the PDF content 😕."

        # Prompt to ask based on PDF content
        prompt = f"""
        You are Mwanga, a helpful assistant for product inquiries. The user is asking: '{user_query}'.
        Use the following PDF content for context:
        
        PDF Content (First 2000 characters):
        {self.pdf_text[:2000]}...
        
        Answer the query based on the above information.
        """
        
        try:
            response = llm.invoke(prompt)
            if self._is_response_relevant(response):
                return self._format_response(response.strip())
            else:
                # Fallback to a general answer from Gemini model
                return self.ask_gemini(user_query)
        except Exception as e:
            return f"Oops, something went wrong 🤖. Error: {e}"

    def ask_gemini(self, user_query):
        """Fallback: Ask the Gemini model for a general answer if PDF doesn't have the answer."""
        fallback_prompt = f"""
        You are a highly knowledgeable assistant. The user is asking: '{user_query}'.
        Since the provided PDF content doesn't have enough information, provide a general and accurate response.
        """
        try:
            response = llm.invoke(fallback_prompt)
            return self._format_response(response.strip())
        except Exception as e:
            return f"Oops, something went wrong 🤖. Error: {e}"

    def _is_response_relevant(self, response):
        """Check if the response generated from the PDF content is relevant or not."""
        # Simple heuristic: check if the response is too generic or empty
        if "I'm not sure" in response or len(response.strip()) < 20:
            return False
        return True

    def _format_response(self, response):
        """Format chatbot responses with fun and friendly tone."""
        human_phrases = [
            "Here's what I found for you 😊:",
            "Ah, I think I have the perfect answer! 👀",
            "Let me break it down for you 📚:",
            "Got it! Here's what I learned 🧠:",
            "Sure thing! Let me explain ✨:"
        ]
        intro = random.choice(human_phrases)
        return f"{intro} {get_random_emoji()}\n\n{response}"

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    """Home page with user form to input info and upload PDF."""
    if request.method == 'POST':
        # Get user data from form
        name = request.form['name']
        company = request.form['company']
        business_sector = request.form['business_sector']
        
        # Save user data in session
        session['name'] = name
        session['company'] = company
        session['business_sector'] = business_sector
        
        # Handle file upload
        if 'pdf_file' not in request.files:
            return "No file part in the request", 400

        pdf_file = request.files['pdf_file']
        if pdf_file.filename == '':
            return "No selected file", 400

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.filename)
        pdf_file.save(file_path)
        
        # Save file path in session for later use
        session['pdf_file_path'] = file_path
        
        return redirect(url_for('chat'))
    
    return render_template('index.html')

@app.route('/chat')
def chat():
    """Chat interface page."""
    return render_template('chat.html')

# WebSocket chat event handling
@socketio.on('user_message')
def handle_user_message(json):
    """Handle messages from the user and generate chatbot response."""
    user_query = json['message']
    pdf_file_path = session.get('pdf_file_path')
    
    # Initialize the chatbot with the PDF file
    chatbot = MwangaChatbot(pdf_file_path)
    
    # Get response from chatbot
    response = chatbot.query_pdf(user_query)
    
    # Send response back to the client
    emit('bot_response', {'response': response})

if __name__ == "__main__":
    # Ensure the upload folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Run in development mode with allow_unsafe_werkzeug=True
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
