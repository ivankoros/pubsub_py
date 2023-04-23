import asyncio
from datetime import datetime
from flask import request
from concurrent.futures import ThreadPoolExecutor
from backend.nlp import vectorized_string_match
import re
import random
from pprint import pprint
from backend.resources import Users
from backend.twilio_app.helpers import (TextResponses, SubOrder, all_sandwiches, generate_user_info,
                                        nearest_interval_time, find_nearest_stores, find_zip,
                                        fuzzy_string_match)
from backend.twilio_app.publix_api import query_deals, find_publix_store_id, find_sub_id

from backend.selenium_app.order_sub_auto import order_sub, OrderSubFunctionDiagnostic
from backend.nlp.order_text_processing import parse_customizations, find_sub_match


# Find/initialize the user
def get_user(session):
    """
    This function finds the user in the database or creates a new user if they don't exist.
     - If they don't exist, initialize them as a user in the database with their phone number
        and their state as 'start'

    Otherwise, just return the user class object, which contains all the user's information
    which I can use to update the user's state and other information.

    :param session: The database session (MySQL)
    :return:        The user class object (contains all the user's information (phone number, name, etc.))
    """
    phone_number = request.values.get("From")
    user = session.query(Users).filter(Users.phone_number == phone_number).first()
    if not user:
        user = Users(phone_number=phone_number,
                     name=None,
                     state='start')
        session.add(user)
        session.commit()
    return user


def start_action(*args):
    """
    This is the state new users start out in if they don't have a name or anything
    else besides their phone number in the database.

    I Send some a welcoming message and prompt them for their name.
    I put them in the 'get_name' state and treat their next message as the input for
    their name.

    :param args:
    :return:
    """
    message_back = state_info['start']['text_response'] + \
                   state_info['get_name']['text_response']

    return 'get_name', message_back


def get_name_action(body, session, user):
    """
    This function uses the body of the user's next message to get their name.

    It treats the user's next message as their name and saves it to the database.

    :param body:  The body of the user's message
    :param session:  The database session
    :param user:  The user class (containing all their info)
    :return:     Putting them into the get_store_location state and calling its text
                 responses
    """
    # Get the user's name and save it to the database
    user.name = body
    session.commit()

    messages = [f"Hey, {user.name}!"] + state_info['get_store_location']['text_response']

    return 'get_store_location', messages


def get_store_location_action(body, session, user):
    # Here I'm calling the find_nearest_stores function to find the (default 3) nearest
    # stores to the user's location with the Google Places and Geolocation APIs and Geopy.
    # I'm passing in the user's given location as the argument.
    nearest_stores = find_nearest_stores(body)

    if len(nearest_stores) != 0:

        # Save the nearest stores to the Users database under
        #   by adding it to the user's nearest_stores column
        user.nearest_stores = nearest_stores
        session.commit()

        """
        This prints out nicely like this:
        
        Here are the nearest stores I found to 1234 Main St:
         
        1. Publix Super Market at Southgate Shopping Center
           Address: 2515 Florida Ave S, Lakeland
           
           ...
        """
        message_back = f"Here are the nearest stores I found to {body}:\n\n"
        for i, store in enumerate(nearest_stores):
            message_back += f"{i + 1}. {store['name']}\n " \
                            f"   Address: {store['address']}\n "

        messages = [message_back] + \
                   ["Which one would you like to order from? "
                    "You can give a number (1) or text confirmation (Yea, St. John's) "
                    "If none of these are correct, say 'redo' and we'll go back a step. "]

        return "confirm_store", messages
    else:
        message_back = ["I didn't find any stores near that location, give me another location "
                        "and I'll try again to find some stores."]

        return "get_store_location", message_back


def confirm_store_action(body, session, user):
    """
            There are two conditions that need to be checked here:
                1. If the user's input is a number, then it's referring to the index of the store
                    in the list of nearest stores. However, all texts come in as a string. Therefore
                    I use regex here to check if the string is a number.

                    If it is a number, then I convert it to an integer and use that to index the
                    list of nearest stores.

                2. If the user's input is a string, then it's referring to the name of the store.
                    I use vectorized string matching to find the closest match to the user's input. By
                    comparing the user's input to the top three store names I gave them.

                If either of these are satisfied, their preferred store location is picked and saved
                to the database.

                Otherwise, the user is prompted to select again, or say 'redo'.

                If they say 'redo', then they are prompted to enter a new location as well.

            """
    if 'redo' not in body:
        store = None

        if re.match(r'^\d+$', body):
            body = int(body)
            store = user.nearest_stores[body - 1]
        else:
            store = fuzzy_string_match(body, [store['name'] for store in user.nearest_stores])
            store = next((s for s in user.nearest_stores if s['name'] == store), None)

        if store:
            """Adding all info of the user's selected store to the database
            
            1. I find the user's zip by using the longitude and latitude of the store
            
            2. I use regex to remove the 'Publix Super Market at ' part of the store name.
            
                The store name coming from the Google Places API always comes in as:
                  'Publix Super Market at <store name>'

                This causes problems because I use the store name to select the store location
                from the Publix website HTML in Selenium. So, I use regex to remove the
                'Publix Super Market at ' part of the store name. 
            
            3. Use the store name and zip code to find the store ID using the Publix API.
            
            4. Save all this info to the database as a JSON object.
            
            """
            longitude, latitude = store['longitude'], store['latitude']
            zip_code = find_zip(longitude, latitude)
            print(f"zip code: {zip_code}")

            store_name = store['name'].replace('Publix Super Market at ', '').strip()
            print(f"store name: {store_name}")

            store_id = find_publix_store_id(zip_code=zip_code,
                                            store_name=store_name)

            user.selected_store = {
                'name': store_name,
                'address': store['address'],
                'zip_code': zip_code,
                'store_id': store_id
            }

            session.commit()

            messages = [f"Great! I'll remember that you want to order from {store_name}.",
                        "You're all set! You can ask me what's on sale to get deals from "
                        "your store or say 'order' to put in an order."]

            return 'default', messages

        else:
            message = [
                "I didn't get that. You can give a number (1) or text confirmation (Yea, St. John's Town Center)",
                "You can also say 'redo' to search for a new location."]
            return 'confirm_store', message
    else:
        message = ["Okay, let's try that again. Give me a location and I'll find the nearest stores."]
        return 'get_store_location', message


def default_action(body, session, user, *args):
    # If the user input is recognized, initialize the default state
    if "order" in body.lower():
        # Todo check for time (store open hours) and give warning if close to closing as well
        return 'order_sub', ["You're all set to order for quick pickup. Give me an order "
                             "and it'll be ready for pickup in 30 minutes.\n\n"
                             "Example: 'Let me get a hot meatball sub with provolone'",
                             "You can also say 'exit' to go back."]

    elif re.search(r"sale|deal|coupon|offer|promotion|special|discount|discounted|discounts",
                   body, re.IGNORECASE):
        # Check if there are any sales today and return the corresponding message
        today_sales = query_deals(user.selected_store['store_id'])

        sub_sale_message = ""

        if len(today_sales) == 1:
            sub_sale_message += f"Looks like the {today_sales[0]['name'].lower().capitalize()} " \
                                f"(${float(today_sales[0]['price']) + 1.50}) is on sale toady."

        elif len(today_sales) > 1:
            sub_list = [f"{sub['name'].lower().capitalize()} (${float(sub['price']) + 1.50})" for sub in today_sales]
            sub_sale_message += f"Looks like the {', '.join(sub_list[:-1])}, and {sub_list[-1]} are on sale today."


        else:
            sub_sale_message = "I didn't find any deals. That is weird, there are always deals." \
                               "This means I might've messed up."

        messages = ["Let's see what's on sale today!", sub_sale_message]

        return 'default', messages

    else:
        return 'default', state_info['default']['text_response']


def order_sub_action(body, session, user, *args):
    """

    """
    if 'exit' in body:
        return 'default', ["You asked to exit, you're now in the default sate. say 'order' to order a sub."]

    if vectorized_string_match(item_to_match=find_sub_match(body), match_possibilities_list=all_sandwiches):

        # If the user's input is determined to be a correct sandwich name, then order the sub
        store_dict = session.query(Users).filter(Users.phone_number == user.phone_number).first().selected_store

        store_name = store_dict['name']
        store_address = store_dict['address']
        store_id = store_dict['store_id']
        order_date = datetime.today().date().strftime("%A, %B %d, %Y")
        order_time = nearest_interval_time()

        general_sub_match = find_sub_match(body)
        sandwich = vectorized_string_match(general_sub_match, all_sandwiches)
        sandwich_id = find_sub_id(store_id=store_id, sub_name=sandwich)

        first_name, last_name, email, phone_number = generate_user_info()

        customization_dictionary = parse_customizations(body)

        pprint(customization_dictionary)

        order = SubOrder(
            sub_name=sandwich,
            sub_id=sandwich_id,
            store_name=store_name,
            store_address=store_address,
            date_of_order=order_date,
            time_of_order=order_time,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            customization_dictionary=customization_dictionary
        )

        def submit_order():
            order_sub(self=order, diagnostic=OrderSubFunctionDiagnostic(),
                      actually_submit=False)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_in_executor(ThreadPoolExecutor(1), submit_order)
        loop.close()

        return 'default', SubOrder.__str__(order)
    else:
        random_sandwiches = [random.choice(all_sandwiches) for _ in range(3)]
        return 'order_sub', [
            f"I don't recognize that as a sub, try again. Some examples include:\n\n"
            f"The {random_sandwiches[0].lower()}, the {random_sandwiches[1].lower()}, and the {random_sandwiches[2].lower()}.",
            f"You can also say 'exit' to exit ordering"]


custom_dict = {'Bread': 'Whole Wheat',
               'Cheese': 'Swiss',
               'Condiments': "Boar's Head Honey Mustard",
               'Extras': 'Hummus',
               'Heating Options': 'Toasted',
               'Make it a Combo': 'None',
               'Size': 'Half',
               'Toppings': 'Banana Peppers, Dill Pickles, Lettuce, Oil & Vinegar Packets'}
# This dictionary contains the state information for the state machine
state_info = {
    'start': {
        'text_response': TextResponses().get_response("start"),
        'action': start_action,
        'next_states': ['get_name']
    },
    'get_name': {
        'text_response': TextResponses().get_response("get_name"),
        'action': get_name_action,
        'next_states': ['get_store_location']
    },
    'get_store_location': {
        'text_response': TextResponses().get_response("get_store_location"),
        'action': get_store_location_action,
        'next_states': ['get_sale']
    },
    'confirm_store': {
        'text_response': "",
        'action': confirm_store_action,
        'next_states': ['get_sale']
    },
    'order_sub': {
        'text_response:': TextResponses().get_response("order_sub"),
        'action': order_sub_action,
        'next_states': ['default, confirm sub']
    },
    'default': {
        'text_response': TextResponses().get_response("default"),
        'action': default_action,
        'next_states': []
    }
}
