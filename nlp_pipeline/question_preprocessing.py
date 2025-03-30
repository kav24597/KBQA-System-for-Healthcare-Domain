import nltk
import sys
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

sys.stdout = open('/dev/null', 'w')
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
sys.stdout = sys.__stdout__

class QuestionPreprocessor:
    def preprocess(self, question):
        tokens = word_tokenize(question.lower())
        tokens = [word for word in tokens if word.isalnum()]
        return " ".join(tokens)

# Example Usage
if __name__ == "__main__":
    preprocessor = QuestionPreprocessor()
    print(preprocessor.preprocess("What are the symptoms of flu?"))
