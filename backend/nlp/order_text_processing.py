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

def find_synonyms(word):
    """Find synonyms of a word using WordNet

    This function is for identifying the meaning of the user's input,
    although they may not have used the correct words. For example,
    if the user says a "meatball hoagie", we still want to be able to
    find and return the "Publix Meatball Sub" sandwich.

    This function takes in a word and follows this process:
    1. Loop over each synonym (syn) in the synset (the group of synonyms) of the word.
    2. Loop over each lemma (the base form of a word) in the synset.
    3. For each lemma, add it to the set of synonyms.

    :param word: string, single word
    :return: list of synonyms for the given word
    """
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return list(synonyms)