import re
import nltk.corpus
from nltk.corpus import stopwords, wordnet
from backend.twilio_app.helpers import all_sandwiches
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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

def find_closest_sandwich_sk(input_to_match, match_list):
    # Clean the user's input
    user_input_clean = clean_text(input_to_match)

    """Convert the sandwich names to TF-IDF vectors

    What I'm doing here is converting each sandwich name into a vector of numbers.
    Each number represents how important that word is to the sandwich name.

    The most highly rated words should be the ones found in our list of subs, so what I do
    is pass the list of subs into the model which will calculate the scores for each word,
    placing more emphasis on the words that are found in the subs.

    This is important because the user's input should be natural:
        "I'm feeling like getting a hot italian today"

    Here, the word "italian", which is in our list of subs, needs to be rated extremely
    high.

    """

    # Initialize the vectorizer and fit it to the list of subs for our model
    vectorizer = TfidfVectorizer()
    sandwich_vectors = vectorizer.fit_transform(match_list)

    # Vectorize the user's input and compare it against the vectorized subs list
    user_vector = vectorizer.transform([user_input_clean])
    similarity_scores = cosine_similarity(user_vector, sandwich_vectors)[0]

    # Find the highest score and return the corresponding sub by index
    best_match_index = similarity_scores.argmax()
    best_match_score = similarity_scores[best_match_index]
    best_match = match_list[best_match_index]

    return best_match if best_match_score >= 0.5 else "No match found"
