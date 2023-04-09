import re
import nltk.corpus
from nltk.corpus import stopwords, wordnet

nltk.download('stopwords')
nltk.download('wordnet')

def clean_text(user_text_input):
    text = user_text_input.lower()

    # Everything that isn't a letter or space is removed
    text = re.sub(r"[^a-zA-Z\s']", "", text)

    # Remove stop words (e.g. "the", "a", "an", "in")
    stop_words = stopwords.words('english')
    text = " ".join([word for word in text.split() if word not in stop_words])

    return text