import googlemaps
import random
import requests
import os
from dotenv import load_dotenv

# These are the text responses that I'm using in a class
class TextResponses:
    def __init__(self):
        self.text_responses = {
            "start": ["Welcome to Sub Deals!.",
                      "Welcome to Sub Deals!."],
            "get_name": ["What's your name?",
                         "What should I call you?"],
            "get_store_location": ["What's your address?",
                                   "Let me know your general location so I can find the nearest store."],
            "get_sale": ["What's on sale today?",
                         "What subs are on sale today?"],
            "default": ["You're in the default state",
                        "You're in the default state"],
            "help": ["Ask me 'any deals today?' to see what subs are on sale today.",
                     "Ask 'what's on sale' to see what on sale today.",
                     "Ask me what's on sale right now to get today's sub deals"],
            "no_sale": "There are no subs on sale today.",
            "error": "Sorry, I don't understand.",
            "sale_prompt": ["deal",
                            "sale",
                            "on sale",
                            "on sale today",
                            "on sale right now",
                            "today's deals",
                            "today's deal"]
        }

    def get_response(self, response):
        return random.choice(self.text_responses[response])



# This is the function that I'm trying to test that takes in the geolocation
# and returns the nearest stores, but I'm not sure how to get the geolocation both
# accurately and naturally (i.e. I don't want to ask for their address + zip code +
# city + state, I just want to ask for a nearby street name or general address)
def find_nearest_stores(location, keyword="Publix", result_count=3):
    load_dotenv()
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location['lat']}%2C{location['lng']}&radius=10000&type=supermarket&keyword={keyword}&key={api_key}"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    response_data = response.json()

    return response_data['results'][:result_count]


# Text cleaning function for NLP input
def clean_text(self):
    text = self.text

    # Lowercase
    text = text.lower()

    # Remove unicode
    text = text.encode("ascii", "ignore").decode()

    pass
