import googlemaps
import random
import requests
import os
from dotenv import load_dotenv
from twilio.rest import Client
import pytz
from datetime import datetime, timedelta
from fuzzywuzzy import process
from geopy.distance import geodesic


"""Static text responses for the bot to send to the user.

    Using the state machine, I can send different messages
    to the user depending on the state. This is a dictionary
    of lists of strings. The keys are the states, and the values
    are the messages that will be sent to the user. 
        
"""

# TODO change this to add methods so a class can be used to
#  put in dynamic messages with f strings
class TextResponses:
    def __init__(self):
        self.text_responses = {
            "start": ["Hey! Glad you've chosen to check out Pubsub Py!"],
            "get_name": ["Can I have your name to start? :)"],
            "get_store_location": ["Let's find your nearest Publix.",
                                   "Give me a location (St. John's Town Center, Jacksonville) "
                                   "or an address (4663 River City Dr) and I'll find the nearest stores."],
            "get_sale": ["Which subs are on sale today?"],
            "default": ["You're in the default state"],
            "help": ["Ask 'any deals today?' to see today's sub deals.",
                     "Ask 'what's on sale' to see what's on sale today.",
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
            "order_sub": ["You would like to order a sub."]
        }

    def get_response(self, response):
        #return random.choice(self.text_responses[response])
        return self.text_responses[response]


class SubOrder:
    def __init__(self, requested_sub, store_name, store_address, date_of_order, first_name,
                 last_name, email, phone_number, time_of_order):
        self.requested_sub = requested_sub
        self.store_name = store_name
        self.store_address = store_address
        self.date_of_order = date_of_order
        self.time_of_order = time_of_order
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number

    def __str__(self):
        return [f"Great, your order for the {self.requested_sub} "
                f"is confirmed for pickup at {self.store_name} " 
                f"at {self.time_of_order} today. "
                f"It'll be ready under the name {self.first_name} {self.last_name}.",

                f"Enjoy your sub! :)"]


class TwilioTexts:
    def __init__(self, phone_number, message):
        self.phone_number = phone_number
        self.message = message

    def twilio_send_msg(self):
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")

        messaging_service_sid = os.getenv("TWILIO_MESSAGING_SERVICE_SID")

        client = Client(account_sid, auth_token)

        client.messages.create(
            messaging_service_sid=messaging_service_sid,
            body=self.message,
            to=self.phone_number)


def generate_user_info():
    """Generate random user info

    This function will generate random user info for each customer.
    The pickup order requires a first name, last name, phone number, and email,
    yet none of this is used to update or inform the customer of their order, besides
    their name which is printed on the receipt that's stapled to the bag.

    So, I've chosen to randomly generate some funny names and emails so the user
    doesn't have to put any of their own information in. This is also a good way to
    test the app with different names and emails to make sure it's working properly.

    """
    suffix_options = ['McGee', 'Yeo', 'Von Humperdink', 'Von Schnitzel',
                      '', '', '', '', '', '', '', '', '', '','']

    first_name_options = ['Wilfred', 'Skipps', 'Rigby', 'Vlad', 'Derwin', 'Yertle', 'Balthazar', 'Bartholomew', 'Looie',
                          'Zooie', 'Finnegan', 'Gulliver', 'Horatio', 'Isadora', 'Jasper', 'Lysander', 'Jo-Jo', 'Mack',
                          'Morris', 'Sneelock', 'Rolf', 'Zinn-a-zu', 'Harry', 'Herbie', 'Hawtch', 'Nutch',
                          'Sneedle', 'Umbus', 'Wump', 'Nook', 'Poozer', 'Luke', 'Foona', 'Norval', 'Doubt-trout']

    last_name_options = ['McBean', 'Vlad-i-Koff', 'Katz', 'Muffinpuff', 'Katzen-bein', 'Cubbins',
                         'McSnazzy', 'Flapdoodle', 'Flibbertigibbet', 'McGrew', 'Who', 'Bar-ba-loots',
                         'McFuzz', 'Mulvaney', 'McCave', 'Wickersham', 'McGurk', 'Joat', 'Yookero',
                         'Sard', 'Potter', 'Haddow', 'Hart', 'Hawtch-Hawtcher', 'Gump', 'Fish', 'Lagoona']

    email_ending_options = ['@aol.com', '@yahoo.com', '@hotmail.com', '@yandex.com', '@bungus.com', '@saxophone.com']

    random_suffix = random.choice(suffix_options)
    random_first_name = random.choice(first_name_options)
    random_last_name = random.choice(last_name_options)

    first_name = f"{random_first_name}"
    last_name = f"{random_last_name} {random_suffix}"

    email = f"{random_first_name.lower()}.{random_last_name.lower()}{random.choice(email_ending_options)}"

    # This is an unused, but valid phone number
    phone_number = '321-556-0291'

    return first_name.strip(), last_name.strip(), email.strip(), phone_number.strip()


def nearest_interval_time(timezone='US/Eastern', length_interval=30, update_interval=5):
    local_tz = pytz.timezone(timezone)
    current_time = datetime.now(local_tz)
    nearest_time = current_time + timedelta(minutes=(length_interval - current_time.minute % update_interval))

    # Split the time into hours and minutes, then remove the leading zero from the hours only
    hour, rest_of_time = nearest_time.strftime("%I:%M %p").split(":", 1)
    formatted_time = hour.lstrip('0') + ":" + rest_of_time

    return formatted_time

def closest_string_match_fuzzy(item_to_match, match_possibilities_list, match_threshold=70):
    # Find the best match using fuzzy string matching
    best_match, score = process.extractOne(item_to_match, match_possibilities_list)

    if score >= match_threshold:
        return best_match
    else:
        # Todo change this to a boolean and update the functions its in
        return "No match found"


# This is the function that I'm trying to test that takes in the geolocation
# and returns the nearest stores, but I'm not sure how to get the geolocation both
# accurately and naturally (i.e. I don't want to ask for their address + zip code +
# city + state, I just want to ask for a nearby street name or general address)
def find_nearest_stores(location, result_count=3):

    maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    google_maps_client = googlemaps.Client(key=maps_api_key)

    geocode_results = google_maps_client.geocode(location)
    user_coordinates = geocode_results[0]['geometry']['location']

    places_result = google_maps_client.places_nearby(location=user_coordinates,
                                                     radius=5000,
                                                     keyword='Publix',
                                                     type='grocery_or_supermarket')

    places = []
    for i, place in enumerate(places_result['results']):
        place_coordinates = place['geometry']['location']
        distance_from_user = geodesic((user_coordinates['lat'],
                                       user_coordinates['lng']),
                                      # We're calculating the distance from the user to each result
                                      (place_coordinates['lat'],
                                       place_coordinates['lng'])).meters

        if "Pharmacy" not in place['name']:
            places.append({
                "name": place['name'],
                "address": place['vicinity'],
                "distance": distance_from_user
            })

    # Sort the results by distance from the user
    places.sort(key=lambda x: x['distance'])

    # Print them out nice :)
    for i, result in enumerate(places):
        print(f"{i + 1}. {result['name']}")
        print(f"   Address: {result['address']}")
        print(f"   Distance: {round(result['distance'])} meters")
        print()

    # Return up to the number of results specified (default is 3)
    return places[:result_count]


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
