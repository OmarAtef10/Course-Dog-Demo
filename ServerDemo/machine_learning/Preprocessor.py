import re
import string
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
import nltk


class Preprocessor:
    def __init__(self) -> None:
        self.stopwords = {
            "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your",
            "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her",
            "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs",
            "themselves", "what", "which", "who", "whom", "this", "that", "these", "those",
            "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
            "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if",
            "or", "because", "as", "until", "while", "of", "at", "by", "for", "with",
            "about", "against", "between", "into", "through", "during", "before", "after",
            "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over",
            "under", "again", "further", "then", "once", "here", "there", "when", "where",
            "why", "how", "all", "any", "both", "each", "few", "more", "most", "other",
            "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too",
            "very", "s", "t", "can", "will", "just", "don", "should", "now"
        }

    def remove_whitespace_fun(self, text):
        return  " ".join(text.split())
    
    def remove_punctuation_fun(self, text):
        translator = str.maketrans('', '', string.punctuation)
        return text.translate(translator)
        
    def remove_numbers_fun(self, text):
        result = re.sub(r'\d+', '', text)
        return result

    def lower_case_fun(self, text):
        return text.lower()
    
    def remove_stopwords_fun(self, text):
        word_tokens = word_tokenize(text)
        filtered_text = [word for word in word_tokens if word not in self.stopwords]
        return ' '.join(filtered_text)

    def stem_words_fun(self, text):
        stemmer = PorterStemmer()
        word_tokens = word_tokenize(text)
        stems = [stemmer.stem(word) for word in word_tokens]
        return ' '.join(stems)  
    
    def __preprocess(self, text):
        if self.remove_whitespace: text = self.remove_whitespace_fun(text)
        if self.remove_punctuation: text = self.remove_punctuation_fun(text)
        if self.remove_numbers:  text = self.remove_numbers_fun(text)
        if self.lower_case: text = self.lower_case_fun(text)
        if self.remove_stopwords: text = self.remove_stopwords_fun(text)
        if self.stem_words: text = self.stem_words_fun(text)
        
        return text
    
    def preprocess_list(self, texts, remove_whitespace=True, remove_punctuation=True, remove_numbers=True, lower_case=True, remove_stopwords=True, stem_words=True):
        out = []
        self.remove_whitespace = remove_whitespace
        self.remove_punctuation = remove_punctuation
        self.remove_numbers = remove_numbers
        self.lower_case = lower_case
        self.remove_stopwords = remove_stopwords
        self.stem_words = stem_words

        for text in texts:
            out.append(
                self.__preprocess(text)
            )
        
        return out
    
    def preprocess_text(self, text, remove_whitespace=True, remove_punctuation=True, remove_numbers=True, lower_case=True, remove_stopwords=True, stem_words=True):
        self.remove_whitespace = remove_whitespace
        self.remove_punctuation = remove_punctuation
        self.remove_numbers = remove_numbers
        self.lower_case = lower_case
        self.remove_stopwords = remove_stopwords
        self.stem_words = stem_words

        return self.__preprocess(text)