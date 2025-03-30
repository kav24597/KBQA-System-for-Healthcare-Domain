import spacy
import logging
from typing import Optional, List, Set

class DiscourseAnalyzer:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logging.error("Spacy model not found. Please run: python -m spacy download en_core_web_sm")
            raise
        
        self.last_topic = None
        self.last_question_type = None
        self.conversation_history = []
        self.known_conditions = {
            "malaria", "diabetes", "cancer", "asthma", "pneumonia", "tuberculosis", 
            "hypertension", "heart disease", "stroke", "arthritis", "depression", 
            "anxiety", "migraine", "allergies", "bronchitis", "flu", "cold",
            "type 1 diabetes", "type 2 diabetes", "high blood pressure", "low blood pressure",
            "heart attack", "kidney disease", "liver disease", "lung disease",
            "typhoid", "typhoid fever", "fever"
        }
        
        # Keywords that indicate follow-up questions
        self.follow_up_keywords = {
            "treatment": "treatment",
            "symptoms": "symptoms",
            "causes": "causes",
            "diagnosis": "diagnosis",
            "prevention": "prevention",
            "risk factors": "risk factors",
            "complications": "complications",
            "medication": "medication",
            "drugs": "medication",
            "medicine": "medication",
            "signs": "symptoms",
            "cure": "treatment",
            "prevent": "prevention",
            "avoid": "prevention",
            "manage": "management",
            "control": "management"
        }

        # Pronouns and context words
        self.context_words = {
            "it", "this", "that", "the condition", "the disease", "the illness",
            "the problem", "the issue", "the infection", "the virus", "the bacteria",
            "they", "them", "their", "its", "these", "those", "the symptoms",
            "the treatment", "the cause", "the diagnosis", "the prevention"
        }

        # Question patterns for better context understanding
        self.question_patterns = {
            "what is": "definition",
            "tell me about": "definition",
            "explain": "definition",
            "describe": "definition",
            "how to": "treatment",
            "how do you": "treatment",
            "what causes": "causes",
            "why does": "causes",
            "what are the symptoms": "symptoms",
            "what are the signs": "symptoms",
            "how is it diagnosed": "diagnosis",
            "how do you know": "diagnosis",
            "how to prevent": "prevention",
            "how can you avoid": "prevention",
            "what are the risk factors": "risk factors",
            "what increases the risk": "risk factors",
            "what are the complications": "complications",
            "what happens if": "complications"
        }

    def resolve_coreferences(self, question: str) -> str:
        """
        Resolve coreferences in the question using context from previous questions.
        
        Args:
            question: The input question string
            
        Returns:
            str: The processed question with resolved coreferences
        """
        if not isinstance(question, str):
            raise ValueError(f"Expected a string as input, but got: {type(question)}")
        
        question = question.strip()
        if not question:
            return question
            
        question_lower = question.lower()
        logging.debug(f"Processing question: {question}")
        
        # First, check if this is a short follow-up question
        if len(question_lower.split()) <= 4 and self.last_topic:
            # Check for question patterns that indicate follow-ups
            question_type = None
            
            # Check prevention-related patterns
            if any(word in question_lower for word in ["prevent", "prevention", "avoid"]):
                question_type = "prevention"
            # Check treatment-related patterns
            elif any(word in question_lower for word in ["treat", "treatment", "cure"]):
                question_type = "treatment"
            # Check symptom-related patterns
            elif any(word in question_lower for word in ["symptom", "sign"]):
                question_type = "symptoms"
            # Check cause-related patterns
            elif any(word in question_lower for word in ["cause", "why"]):
                question_type = "causes"
            # Check severity/danger patterns
            elif any(word in question_lower for word in ["serious", "dangerous", "severe"]):
                question_type = "severity"
            
            if question_type:
                if question_type == "severity":
                    resolved_question = f"How severe is {self.last_topic}?"
                else:
                    resolved_question = f"What are the {question_type}s of {self.last_topic}?"
                self.conversation_history.append((self.last_topic, question_type))
                logging.debug(f"Resolved short follow-up to: {resolved_question}")
                return resolved_question
        
        # Extract medical topics from the current question
        doc = self.nlp(question)
        current_topics = []
        
        # Look for medical conditions in the text
        for token in doc:
            if token.text.lower() in self.known_conditions:
                current_topics.append(token.text.lower())
                logging.debug(f"Found medical condition: {token.text}")
        
        # Check for compound conditions (e.g., "typhoid fever")
        text = question_lower
        for condition in self.known_conditions:
            if condition in text:
                current_topics.append(condition)
                logging.debug(f"Found condition: {condition}")
        
        # If we found topics in the current question, update our state
        if current_topics:
            self.last_topic = current_topics[-1]  # Use the last mentioned condition
            self.conversation_history.append((self.last_topic, "topic"))
            logging.debug(f"Updated last topic to: {self.last_topic}")
            return question
        
        # Handle follow-up questions with pronouns or implicit context
        has_context_word = any(word in question_lower for word in self.context_words)
        question_type = None

        # Determine question type from keywords
        for keyword, q_type in self.follow_up_keywords.items():
            if keyword in question_lower:
                question_type = q_type
                break
        
        # If we have a last topic and either a context word or a question type, treat as follow-up
        if self.last_topic and (has_context_word or question_type):
            if not question_type:
                # Try to infer question type from the question
                if "how" in question_lower:
                    question_type = "treatment"
                elif "why" in question_lower:
                    question_type = "causes"
                elif "what" in question_lower:
                    question_type = "definition"
                elif any(word in question_lower for word in ["serious", "dangerous", "severe"]):
                    question_type = "severity"
                else:
                    question_type = "information"
            
            if question_type == "severity":
                resolved_question = f"How severe is {self.last_topic}?"
            else:
                resolved_question = f"What are the {question_type}s of {self.last_topic}?"
            self.conversation_history.append((self.last_topic, question_type))
            logging.debug(f"Resolved follow-up question to: {resolved_question}")
            return resolved_question
        
        logging.debug(f"Returning original question: {question}")
        return question

    def get_conversation_context(self) -> List[tuple]:
        """
        Get the conversation history for context.
        
        Returns:
            List[tuple]: List of (topic, question_type) pairs
        """
        return self.conversation_history

    def clear_context(self):
        """Clear the conversation context."""
        self.last_topic = None
        self.last_question_type = None
        self.conversation_history = []
        logging.debug("Cleared conversation context")

# Example Usage
if __name__ == "__main__":
    analyzer = DiscourseAnalyzer()
    
    # Test basic queries
    print(analyzer.resolve_coreferences("What are the symptoms of malaria?"))
    print(analyzer.resolve_coreferences("What is the treatment?"))
    print(analyzer.resolve_coreferences("How is it diagnosed?"))
    
    # Test with different conditions
    print(analyzer.resolve_coreferences("Tell me about diabetes"))
    print(analyzer.resolve_coreferences("What are the risk factors?"))
    
    # Test with pronouns
    print(analyzer.resolve_coreferences("What causes this condition?"))
    
    # Clear context and test again
    analyzer.clear_context()
    print(analyzer.resolve_coreferences("What are the symptoms of asthma?"))
