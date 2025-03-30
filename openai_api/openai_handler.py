import openai
import os
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class OpenAIHandler:
    def __init__(self):
        # Check for OpenAI API key
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
            
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Expanded medical keywords for better detection
        self.medical_keywords = {
            # General medical terms
            "disease", "treatment", "symptoms", "medicine", "doctor", "health",
            "diagnosis", "patient", "medical", "clinical", "hospital", "therapy",
            "condition", "illness", "infection", "surgery", "prescription",
            "medication", "cure", "prevention", "healthcare", "virus", "bacteria",
            "chronic", "acute", "pain", "blood", "heart", "brain", "immune",
            
            # Common conditions
            "diabetes", "cancer", "asthma", "arthritis", "depression", "anxiety",
            "hypertension", "allergy", "migraine", "flu", "cold", "fever",
            
            # Body parts and systems
            "head", "chest", "stomach", "back", "joints", "muscles", "bones",
            "skin", "lungs", "liver", "kidney", "nervous", "digestive", "respiratory",
            
            # Symptoms and signs
            "pain", "ache", "swelling", "rash", "cough", "fever", "nausea",
            "dizziness", "fatigue", "weakness", "numbness", "headache",
            
            # Medical procedures
            "test", "scan", "xray", "mri", "examination", "checkup", "vaccination",
            "screening", "surgery", "operation", "treatment", "therapy",
            
            # Healthcare terms
            "doctor", "nurse", "specialist", "physician", "hospital", "clinic",
            "emergency", "ambulance", "pharmacy", "medicine", "drug", "prescription"
        }
        
        # System prompt to ensure medical focus
        self.system_prompt = """You are a knowledgeable medical assistant. Your role is to:
1. Answer ALL health and medical-related questions comprehensively
2. Provide accurate, evidence-based medical information
3. Include important disclaimers when necessary
4. Maintain a professional and clear communication style
5. Refer to proper medical consultation when appropriate

Important guidelines:
- Answer any question related to health, medicine, or healthcare
- Always include a medical disclaimer for advice-related questions
- Provide comprehensive but understandable explanations
- Include relevant medical terminology with plain language explanations
- Focus on factual, scientifically-backed information
- Structure responses clearly with sections when appropriate
- Use bullet points or numbered lists for better readability
- Always err on the side of answering medical questions, even if the connection is indirect"""

    def is_medical_query(self, query: str) -> bool:
        """
        Determines if the query is medical-related using enhanced keyword matching and context analysis.
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Check for medical keywords
        if any(keyword in query_lower for keyword in self.medical_keywords):
            return True
            
        # Check for medical condition mentions
        if any(word.endswith(('itis', 'osis', 'emia', 'algia', 'pathy', 'oma')) for word in query_words):
            return True
            
        # Check for health-related question patterns
        health_patterns = [
            "what causes", "how to treat", "symptoms of", "signs of",
            "is it normal", "should i see", "what doctor", "how long",
            "what happens", "side effects", "how do you", "what are",
            "tell me about", "explain", "describe", "define"
        ]
        if any(pattern in query_lower for pattern in health_patterns):
            return True
            
        return False

    def query_openai(self, question: str) -> str:
        """
        Queries OpenAI with proper medical context and validation.
        """
        try:
            logger.debug(f"Sending query to OpenAI: {question}")
            
            # Add context to the question if needed
            enhanced_question = question
            if not any(word in question.lower() for word in ["what is", "define", "explain", "tell me about"]):
                enhanced_question = f"In medical terms, {question}"
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": enhanced_question}
                ],
                temperature=0.7,
                max_tokens=800  # Increased for more comprehensive responses
            )
            
            answer = response.choices[0].message.content.strip()
            logger.debug(f"Received response from OpenAI: {answer}")
            
            # Add medical consultation disclaimer
            disclaimer = "\n\nPlease note: This information is for educational purposes only. Always consult with a healthcare professional for personal medical advice."
            if not answer.endswith(disclaimer):
                answer += disclaimer
            
            return answer

        except Exception as e:
            logger.error(f"Error querying OpenAI: {str(e)}")
            return "I apologize, but I encountered an error while processing your question. Please try asking again."

    def format_medical_response(self, response: str) -> str:
        """
        Formats the medical response for better readability and clarity.
        """
        # Split response into sections if it contains multiple sentences
        sentences = response.split('. ')
        
        if len(sentences) > 3:
            # Format longer responses with sections
            first_sentence = sentences[0]
            body_sentences = sentences[1:-1]  # Exclude disclaimer
            disclaimer = sentences[-1]
            
            # Group body sentences into paragraphs
            paragraphs = []
            current_paragraph = []
            
            for sentence in body_sentences:
                current_paragraph.append(sentence)
                if len(current_paragraph) == 2:  # Adjust paragraph size as needed
                    paragraphs.append('. '.join(current_paragraph) + '.')
                    current_paragraph = []
            
            if current_paragraph:
                paragraphs.append('. '.join(current_paragraph) + '.')
            
            # Format the response with better structure
            formatted_response = f"📋 {first_sentence}:\n\n"
            
            # Add bullet points for key points
            key_points = []
            for para in paragraphs:
                if any(word in para.lower() for word in ['include', 'consist', 'have', 'are', 'is']):
                    key_points.append(f"• {para}")
                else:
                    key_points.append(para)
            
            formatted_response += '\n\n'.join(key_points)
            
            # Add a separator before the disclaimer
            formatted_response += "\n\n" + "─" * 50 + "\n\n"
            formatted_response += f"⚠️ {disclaimer}"
            
            return formatted_response
            
        return response
