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


# All possible customization tops for Publix subs
customizations = {
    "size": {
        "half": "Half",
        "whole": "Whole"
    },
    "bread": {
        "italian_5_grain": "Italian 5 Grain",
        "white": "White",
        "whole_wheat": "Whole Wheat",
        "flatbread": "Flatbread",
        "no_bread_lettuce": "No Bread (Make it a Salad) - Lettuce Base",
        "no_bread_spinach": "No Bread (Make it a Salad) - Spinach Base"
    },
    "cheese": {
        "pepper_jack": "Pepper Jack",
        "cheddar": "Cheddar",
        "muenster": "Muenster",
        "provolone": "Provolone",
        "swiss": "Swiss",
        "white_american": "White American",
        "yellow_american": "Yellow American",
        "no_cheese": "No Cheese"
    },
    "extras": {
        "double_meat": "Double Meat",
        "double_cheese": "Double Cheese",
        "bacon": "Bacon",
        "guacamole": "Guacamole",
        "hummus": "Hummus",
        "avocado": "Avocado"
    },
    "toppings": {
        "banana_peppers": "Banana Peppers",
        "black_olives": "Black Olives",
        "boars_head_garlic_pickles": "Boar's Head Garlic Pickles",
        "cucumbers": "Cucumbers",
        "dill_pickles": "Dill Pickles",
        "green_peppers": "Green Peppers",
        "jalapeno_peppers": "Jalapeno Peppers",
        "lettuce": "Lettuce",
        "onions": "Onions",
        "spinach": "Spinach",
        "tomato": "Tomato",
        "salt": "Salt",
        "black_pepper": "Black Pepper",
        "oregano": "Oregano",
        "oil_vinegar_packets": "Oil & Vinegar Packets"
    },
    "condiments": {
        "boars_head_honey_mustard": "Boar's Head Honey Mustard",
        "boars_head_spicy_mustard": "Boar's Head Spicy Mustard",
        "mayonnaise": "Mayonnaise",
        "yellow_mustard": "Yellow Mustard",
        "vegan_ranch_dressing": "Vegan Ranch Dressing",
        "buttermilk_ranch": "Buttermilk Ranch",
        "boars_head_sub_dressing": "Boar's Head Sub Dressing",
        "boars_head_pepperhouse_gourmaise": "Boar's Head Pepperhouse Gourmaise",
        "boars_head_chipotle_gourmaise": "Boar's Head Chipotle Gourmaise",
        "deli_sub_sauce": "Deli Sub Sauce"
    },
    "heating_options": {
        "pressed": "Pressed",
        "toasted": "Toasted",
        "no_thanks": "No Thanks"
    },
    "make_it_a_combo": {
        "yes": "Yes",
        "no_thanks": "No Thanks"
    }
}
