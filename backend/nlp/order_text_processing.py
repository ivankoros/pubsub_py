import re
import nltk.corpus
from nltk.corpus import stopwords, wordnet
from backend.twilio_app.helpers import all_sandwiches
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import openai
import os
import ast
from pprint import pprint
from dotenv import load_dotenv

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


def find_closest_sandwich_sk(item_to_match, match_possibilities_list=all_sandwiches):
    # Clean the user's input
    user_input_clean = clean_text(item_to_match)

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
    sandwich_vectors = vectorizer.fit_transform(match_possibilities_list)

    # Vectorize the user's input and compare it against the vectorized subs list
    user_vector = vectorizer.transform([user_input_clean])
    similarity_scores = cosine_similarity(user_vector, sandwich_vectors)[0]

    # Find the highest score and return the corresponding sub by index
    best_match_index = similarity_scores.argmax()
    best_match_score = similarity_scores[best_match_index]
    best_match = match_possibilities_list[best_match_index]

    return best_match if best_match_score >= 0.5 else "No match found"

def get_order(user_order_text):

    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", 'config\\.env'))

    load_dotenv(dotenv_path=ROOT_DIR,
                override=True)

    openai.api_key = os.getenv("OPEN_AI_API_KEY")

    messages = [
        {
            "role": "system",
            "content": (
                "Based on the following list of customization options: \n"
                "Size: Half, Whole \n"
                "Bread: Italian 5 Grain, White, Whole Wheat, Flatbread, No Bread (Make it a Salad) - Lettuce Base, No Bread (Make it a Salad) - Spinach Base\n"
                "Cheese: Pepper Jack, Cheddar, Muenster, Provolone, Swiss, White American, Yellow American, No Cheese\n"
                "Extras: Double Meat, Double Cheese, Bacon, Guacamole, Hummus, Avocado\n"
                "Toppings: Banana Peppers, Black Olives, Boar's Head Garlic Pickles, Cucumbers, Dill Pickles, Green Peppers, Jalapeno Peppers, Lettuce, Onions, Spinach, Tomato, Salt, Black Pepper, Oregano, Oil & Vinegar Packets\n"
                "Condiments: Boar's Head Honey Mustard, Boar's Head Spicy Mustard, Mayonnaise, Yellow Mustard, Vegan Ranch Dressing, Buttermilk Ranch, Boar's Head Sub Dressing, Boar's Head Pepperhouse Gourmaise, Boar's Head Chipotle Gourmaise, Deli Sub Sauce\n"
                "Heating Options: Pressed, Toasted, No Thanks\n"
                "Make it a Combo: Yes, No Thanks\n"
                "\n"
                "If a field is not specified, reply with 'None' Only. There should only be 8 category outputs, absolutely no more. If there are duplicates (for example, "
                " two 'condiments' rows), consolidate them.\n"
                "If a user has 'packets' in their message, they want the 'Oil & Vinegar Packets' topping\n"
                "Follow this rule strictly: Return customization options exactly as they appear in the text. For example 'sub oil' should return 'Deli Sub Sauce'\n"
                "\n"
                "Give back a list of selected customization options from the user's text input, which is a sandwich order\n\n"
                "Return the list back as a Python dictionary, with the keys being the category and the values being the selected options. \n"
            ),
        },
        {"role": "user", "content": f"Sandwich order: {user_order_text}"}
    ]

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.1,
    )

    response = completion.choices[0].message['content']

    try:
        print(f"Order: {user_order_text}")
        print(f"String respoonse: {response}")
        print("\n")
        pprint(ast.literal_eval(response))
        return ast.literal_eval(response)
    except (ValueError, SyntaxError) as e:
        print("Error:", e)