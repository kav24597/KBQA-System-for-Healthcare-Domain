import os
import warnings
import sys
import tkinter as tk
import logging
from tkinter import scrolledtext
from tkinter import ttk
from tkinter import font as tkfont

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure we're running from the project root directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from models.kg_query_handler import KnowledgeBase
from models.discourse_analyzer import DiscourseAnalyzer
from models.pragmatic_handler import PragmaticHandler
from nlp_pipeline.question_preprocessing import QuestionPreprocessor
from nlp_pipeline.intent_classifier import IntentClassifier
from openai_api.openai_handler import OpenAIHandler

# Suppress only OwlReady2 logs (not everything)
stderr_backup = sys.stderr
stdout_backup = sys.stdout
sys.stderr = open(os.devnull, "w")

warnings.filterwarnings("ignore")
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Initialize KBQA Components
kb = KnowledgeBase()
discourse = DiscourseAnalyzer()
pragmatics = PragmaticHandler()
preprocessor = QuestionPreprocessor()
classifier = IntentClassifier()

try:
    openai_api = OpenAIHandler()
    openai_available = True
except ValueError as e:
    logger.warning(f"OpenAI initialization failed: {str(e)}")
    openai_available = False
except Exception as e:
    logger.error(f"Unexpected error initializing OpenAI: {str(e)}")
    openai_available = False

# Restore normal stdout/stderr for debugging
sys.stderr = stderr_backup
sys.stdout = stdout_backup

def process_query():
    """Handles user input, processes the query, and displays the response."""
    question = entry.get().strip()  # Get user input

    if not question:
        return  # Do nothing if input is empty

    if question.lower() == "exit":
        root.destroy()  # Close window on exit command
        return

    try:
        # Display user's question
        display_user_message(question)
        
        # Step 1: Discourse Analysis (Coreference Resolution)
        processed_question = discourse.resolve_coreferences(question)
        logger.debug(f"After discourse analysis: {processed_question}")
        
        # Show interpretation if question was modified
        if processed_question != question:
            display_system_message(f"(I understand you're asking about: {processed_question})")
            
        # Get conversation context
        context = discourse.get_conversation_context()
        if context:
            last_topic, last_type = context[-1]
            logger.debug(f"Current context - Topic: {last_topic}, Type: {last_type}")
            
            # If we have context but no explicit topic in the current question,
            # make sure to use the last topic
            if last_topic and "it" in processed_question.lower():
                processed_question = processed_question.lower().replace("it", last_topic)
                logger.debug(f"Updated question with context: {processed_question}")

        # Step 2: Check if OpenAI is available
        if not openai_available:
            display_system_message("I apologize, but I'm currently unable to process medical queries as the OpenAI service is not available. Please ensure the OPENAI_API_KEY environment variable is set.")
            return

        # Step 3: Get response from OpenAI
        try:
            # Check if the question needs clarification through pragmatic analysis
            pragmatic_response = pragmatics.infer_intended_meaning(processed_question)
            if pragmatic_response and "please specify" in pragmatic_response.lower():
                display_system_message(pragmatic_response)
                return
                
            response = openai_api.query_openai(processed_question)
            formatted_response = openai_api.format_medical_response(response)
            display_system_message(formatted_response)
            
        except Exception as e:
            logger.error(f"Error getting OpenAI response: {str(e)}")
            display_system_message("I apologize, but I encountered an error while processing your query. Please try asking again.")

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        display_system_message("Sorry, I encountered an error while processing your query. Please try again.")

def display_user_message(message):
    """Displays user message in the chat box with better formatting."""
    chat_box.config(state=tk.NORMAL)
    chat_box.insert(tk.END, "\n", "spacing")
    chat_box.insert(tk.END, "👤 You: ", "user_label")
    chat_box.insert(tk.END, f"{message}\n", "user_message")
    chat_box.config(state=tk.DISABLED)
    chat_box.see(tk.END)
    entry.delete(0, tk.END)  # Clear input box

def display_system_message(message):
    """Displays system message in the chat box with better formatting."""
    chat_box.config(state=tk.NORMAL)
    chat_box.insert(tk.END, "\n", "spacing")
    chat_box.insert(tk.END, "🤖 KBQA System: ", "bot_label")
    chat_box.insert(tk.END, f"{message}\n", "bot_message")
    chat_box.config(state=tk.DISABLED)
    chat_box.see(tk.END)

# Create main Tkinter window
root = tk.Tk()
root.title("Medical KBQA System")
root.geometry("900x700")
root.minsize(900, 700)

# Set window background color
root.configure(bg="#f5f6fa")

# Configure styles
style = ttk.Style()
style.configure("TFrame", background="#f5f6fa")
style.configure("TButton", 
    padding=10,
    font=("Helvetica", 12),
    background="#4a90e2",
    foreground="white"
)
style.configure("TEntry", 
    padding=10,
    font=("Helvetica", 12)
)

# Create main container with gradient effect
main_container = ttk.Frame(root)
main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

# Title label with modern styling
title_label = tk.Label(
    main_container,
    text="Medical Knowledge Base QA System",
    font=("Helvetica", 24, "bold"),
    bg="#f5f6fa",
    fg="#2c3e50"
)
title_label.pack(pady=(0, 20))

# Chat display box with modern styling
chat_box = scrolledtext.ScrolledText(
    main_container,
    wrap=tk.WORD,
    font=("Helvetica", 12),
    height=25,
    width=80,
    bg="#ffffff",
    fg="#2c3e50",
    padx=15,
    pady=15,
    relief="flat",
    borderwidth=0
)
chat_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Configure text tags for different message types
chat_box.tag_config("spacing", spacing1=10, spacing3=10)
chat_box.tag_config("user_label", 
    foreground="#4a90e2",
    font=("Helvetica", 12, "bold"),
    spacing1=5
)
chat_box.tag_config("user_message", 
    foreground="#2c3e50",
    font=("Helvetica", 12),
    spacing1=5
)
chat_box.tag_config("bot_label", 
    foreground="#27ae60",
    font=("Helvetica", 12, "bold"),
    spacing1=5
)
chat_box.tag_config("bot_message", 
    foreground="#2c3e50",
    font=("Helvetica", 12),
    spacing1=5
)

# Frame for input and button with modern styling
input_frame = ttk.Frame(main_container)
input_frame.pack(pady=20, fill=tk.X)

# User input box with modern styling
entry = ttk.Entry(
    input_frame,
    width=70,
    font=("Helvetica", 12)
)
entry.pack(side=tk.LEFT, padx=10, pady=5, expand=True, fill=tk.X)
entry.bind('<Return>', lambda e: process_query())

# Submit button with modern styling
submit_button = ttk.Button(
    input_frame,
    text="Ask",
    command=process_query,
    width=10,
    style="Accent.TButton"
)
submit_button.pack(side=tk.RIGHT, padx=10)

# Create a custom style for the submit button
style.configure("Accent.TButton",
    background="#4a90e2",
    foreground="white",
    padding=10,
    font=("Helvetica", 12, "bold")
)

# Add a subtle border to the chat box
chat_box.configure(highlightthickness=1, highlightbackground="#e1e1e1")

# Initial system message with welcome animation
display_system_message("👋 Welcome to your Medical Knowledge Assistant!\n\nI'm here to help you with any health-related questions. Feel free to ask about:\n• Medical conditions and symptoms\n• Treatments and medications\n• Prevention and lifestyle\n• General health information\n\nHow can I assist you today?")

# Run Tkinter event loop
root.mainloop()
