import string
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords

porter = PorterStemmer()

def remove_punctuation(text):
    '''
    Removes punctuation from text

    :param text:
    :return:
    '''
    return "".join([char if char not in string.punctuation else ' ' for char in text])

def remove_stopwords(text):
    words = text.split()
    return " ".join([word for word in words if word not in stopwords.words('english')])

def remove_short_long_words(text):
    words = text.split()
    return " ".join([word for word in words if (1 < len(word) < 25)])

def remove_non_alphanumeric_words(text):
    words = text.split()
    return " ".join([word for word in words if word.isalnum()])

def stem_words(words):
    return " ".join([porter.stem(word) for word in words])

def preprocess_review(review):
    review = str(review)
    review = review.strip()
    review = review.lower()
    review = remove_punctuation(review)
    # review = remove_short_long_words(review)
    # review = remove_non_alphanumeric_words(review)
    review = remove_stopwords(review)
    return stem_words(review.split())
