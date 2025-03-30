class PragmaticHandler:
    def __init__(self):
        # Expanded medical keywords
        self.medical_keywords = {
            # Common medical terms
            "symptoms", "treatment", "medicine", "disease", "doctor", "fever",
            "cancer", "diabetes", "infection", "antibiotics", "therapy",
            "surgery", "blood pressure", "prescription", "vaccine",
            
            # Symptoms and conditions
            "pain", "ache", "swelling", "rash", "cough", "nausea",
            "dizziness", "fatigue", "weakness", "headache", "anemia",
            
            # Body parts
            "head", "chest", "stomach", "back", "joints", "muscles",
            "heart", "lungs", "liver", "kidney", "brain",
            
            # Common phrases
            "how to", "what causes", "is it normal", "should i",
            "can i", "when to", "how long", "what about"
        }
        
        # Common medical context patterns
        self.context_patterns = {
            "treatment_seeking": [
                "should i see", "do i need", "when to visit",
                "is it serious", "should i worry"
            ],
            "symptom_checking": [
                "is it normal", "what does it mean", "why do i",
                "how to know", "what if"
            ],
            "medication_related": [
                "can i take", "how to use", "side effects",
                "is it safe", "how much"
            ]
        }

        # Add greetings and farewells
        self.greetings = {
            "hi", "hello", "hey", "good morning", "good afternoon", 
            "good evening", "greetings", "howdy"
        }
        
        self.farewells = {
            "bye", "goodbye", "see you", "farewell", "good night",
            "take care", "have a good day", "bye bye"
        }

    def infer_intended_meaning(self, query):
        """
        Handles implicit queries and adds medical context when needed.
        """
        if not isinstance(query, str):
            raise ValueError("Error: query must be a string!")
            
        query_lower = query.lower()
        
        # Check for greetings and farewells first
        if any(greeting in query_lower for greeting in self.greetings):
            return "Hello! I'm your medical assistant. How can I help you today?"
            
        if any(farewell in query_lower for farewell in self.farewells):
            return "Goodbye! Take care and stay healthy!"
        
        # Handle treatment-seeking patterns
        if any(pattern in query_lower for pattern in self.context_patterns["treatment_seeking"]):
            if not any(keyword in query_lower for keyword in self.medical_keywords):
                return "Please specify which medical condition you're concerned about."
        
        # Handle severity questions
        if ("is it dangerous" in query_lower or "is it serious" in query_lower or 
            "how severe" in query_lower) and not any(keyword in query_lower for keyword in self.medical_keywords):
            return "Please specify which condition or symptom you're concerned about."
        
        # Handle general prevention questions
        if "how can i avoid getting sick" in query_lower or "how to prevent illness" in query_lower:
            return "Here are some general prevention tips: maintain good hygiene, get regular exercise, eat a balanced diet, get enough sleep, and stay up to date with vaccinations. For specific conditions, please ask about them directly."
        
        # Handle specific prevention questions without context
        if ("how to prevent" in query_lower or "how do i avoid" in query_lower) and not any(keyword in query_lower for keyword in self.medical_keywords):
            return "Please specify which condition you'd like to prevent."
        
        # Handle general medical advice questions
        if "what should i do" in query_lower and not any(keyword in query_lower for keyword in self.medical_keywords):
            return "Please provide more details about your medical concern. What symptoms or condition are you asking about?"
        
        # For medical queries with context, let them proceed
        if self.filter_query(query_lower):
            return None
            
        return None

    def _add_medical_context(self, query, context_type):
        """
        Adds medical context to ambiguous queries.
        """
        if context_type == "treatment":
            return f"Note: For specific treatment advice, please provide details about the condition. {query}"
        elif context_type == "symptoms":
            return f"To better understand your symptoms, please provide more details. {query}"
        elif context_type == "medication":
            return f"For medication-related advice, please specify the medicine and condition. {query}"
        return query

    def filter_query(self, question):
        """
        Checks if the question is healthcare-related using expanded criteria.
        """
        question_lower = question.lower()
        
        # Check direct keyword matches
        if any(keyword in question_lower for keyword in self.medical_keywords):
            return True
            
        # Check medical patterns
        for pattern_list in self.context_patterns.values():
            if any(pattern in question_lower for pattern in pattern_list):
                return True
                
        # Check for medical suffixes
        words = question_lower.split()
        medical_suffixes = ('itis', 'osis', 'emia', 'algia', 'pathy', 'oma')
        if any(word.endswith(medical_suffixes) for word in words):
            return True
            
        return False

# Example Usage
if __name__ == "__main__":
    pragmatics = PragmaticHandler()
    print(pragmatics.infer_intended_meaning("Can I eat sweets?"))  # Expected: "Are you diabetic?..."
    print(pragmatics.filter_query("What is the capital of France?"))  # Expected: False
    print(pragmatics.filter_query("What are the symptoms of diabetes?"))  # Expected: True
