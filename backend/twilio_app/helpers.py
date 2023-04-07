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
                            "today's deal"],
            "order_sub": ["You would like to order a sub.",
                          "You would like to order a sub."]
        }

    def get_response(self, response):
        return random.choice(self.text_responses[response])

class SubOrder:
    def __init__(self, requested_sub, store_name, date_of_order):
        self.requested_sub = requested_sub
        self.store_name = store_name
        self.date_of_order = date_of_order

    # Order confirmation feedback
        self.first_name = None
        self.last_name = None
        self.ordered_sandwich_name = None
        self.time_of_order = None

    def order_feedback(self):
        return f"Great, your order for the {self.ordered_sandwich_name} " \
               f"is confirmed for pickup at {self.store_name} " \
               f"at {self.time_of_order} today. " \
               f"It'll be ready under the name {self.first_name} {self.last_name}.\n" \
               f"Enjoy your sub! :)"

    def __repr__(self):
        return f"Name of sub: {self.requested_sub}\n" \
               f"Store location: {self.store_name} \n" \
               f"Date of order: {self.date_of_order}"

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
all_customizations = {
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

all_sandwiches = [
    "Boar's Head Ultimate Sub",
    "Boar's Head Turkey Sub",
    "Publix Italian Sub",
    "Publix Chicken Tender Sub",
    "Boar's Head Italian Sub",
    "Publix Turkey Sub",
    "Boar's Head Ham Sub",
    "Boar's Head Italian Wrap",
    "Publix Veggie Sub",
    "Boar's Head Maple Honey Turkey Sub",
    "Boar's Head Roast Beef Sub",
    "Publix Ultimate Sub",
    "Publix Turkey Wrap",
    "Boar's Head Ultimate Wrap",
    "Publix Veggie Wrap",
    "Chicken Cordon Bleu Sub Hot",
    "Boar's Head Honey Turkey Wrap",
    "Boar's Head Jerk Turkey & Gouda Sub",
    "Publix Tuna Salad Sub",
    "Publix Homestyle Beef Meatball Sub",
    "Publix Italian Wrap",
    "Boar's Head Roast Beef Wrap",
    "Publix Ham Sub",
    "Boar's Head Ham and Turkey Sub",
    "Publix Deli Spicy Falafel Sub Wrap Hot",
    "Publix Roast Beef Sub",
    "Publix Ultimate Wrap",
    "Publix Chicken Salad Wrap",
    "Boar's Head Everroast Wrap",
    "Publix Deli Spicy Falafel Sub",
    "Boar's Head Philly Cheese Sub",
    "Boar's Head Havana Bold Sub",
    "Boar's Head EverRoast Sub",
    "Publix Deli Tex Mex Black Bean Burger Sub",
    "Publix Ham Wrap",
    "Boar's Head Low Sodium Ultimate Sub",
    "Boar's Head Philly Wrap",
    "Publix Ham & Turkey Sub",
    "Publix Greek Sub",
    "Publix Deli Meatless Turkey Club Sub",
    "Boar's Head Ham Wrap",
    "Publix Roast Beef Wrap",
    "Publix Egg Salad Wrap",
    "Publix Deli Baked Chicken Tender Wrap",
    "Publix Deli Baked Chicken Tender Sub",
    "Publix Tuna Salad Wrap",
    "Boar's Head BLT Hot Sub",
    "Boar's Head Low Sodium Turkey Sub",
    "Boar's Head Blt Wrap",
    "Publix Chicken Salad Sub",
    "Publix Philly Cheese Sub",
    "Publix Egg Salad Sub",
    "Publix Deli Meatless Turkey Club Sub Wrap",
    "Publix Deli Tex Mex Black Bean Burger Wrap",
    "Publix Cuban Sub",
    "Publix Deli Ham Salad Sub",
    "Boar's Head Cajun Turkey Sub",
    "Boar's Head Chipotle Chicken Wrap",
    "Boar's Head Cracked Pepper Turkey Sub",
    "Publix Deli Nashville Hot Chicken Tender Sub",
    "Publix Deli Nashville Hot Chicken Tender Wrap",
    "Reuben - Corned Beef",
    "Publix Garlic and Herb Tofu Sub",
    "Reuben - Turkey",
    "Publix Deli Greek Wrap",
    "Publix Deli Meatless Turkey Club Sub Wrap Hot",
    "Publix Ham Salad Wrap",
    "Boar's Head Deluxe Sub",
    "Publix Ham and Turkey Wrap",
    "Boar's Head Deluxe Wrap",
    "Publix Cuban Wrap",
    "Boar's Head American Wrap",
    "Boar's Head Low Sodium Ham Sub",
    "Boar's Head American Sub",
    "Publix Deli Mojo Pork Sub",
    "Boar's Head Cajun Turkey Wrap",
    "Boar's Head Chipotle Chicken Sub",
    "Boar's Head Cracked Pepper Turkey Wrap",
    "Publix Deli Meatless Philly Sub Hot"
]

