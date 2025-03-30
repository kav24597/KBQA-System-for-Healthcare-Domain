from transformers import pipeline
import transformers
import logging
import os

# Suppress Hugging Face & PyTorch warnings
transformers.logging.set_verbosity_error()
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # TensorFlow
os.environ["TRANSFORMERS_VERBOSITY"] = "error"  # Hugging Face
os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Suppress tokenizer warnings

class IntentClassifier:
    def __init__(self):
        self.model = pipeline("text-classification", model="distilbert-base-uncased")

    def classify_intent(self, question):
        result = self.model(question)
        return result[0]['label']

# Example Usage
if __name__ == "__main__":
    classifier = IntentClassifier()
    print(classifier.classify_intent("What is the treatment for flu?"))
