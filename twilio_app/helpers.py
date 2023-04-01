import googlemaps
import random
import os
from dotenv import load_dotenv

# These are the text responses that I'm using in a class
class TextResponses:
    def __init__(self):
        self.text_responses = {
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

def find_nearest_stores(location, keyword="Publix"):

    load_dotenv()
    gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))

    result = gmaps.places_nearby(location=location, radius=10000, keyword=keyword)
    return result['results'][:3]
