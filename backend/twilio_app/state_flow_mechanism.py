import time
import asyncio
from datetime import datetime, timedelta
from flask import Flask, Response, request
from concurrent.futures import ThreadPoolExecutor
import re

from backend.resources import SubDeal
from backend.resources import Users
from backend.twilio_app.helpers import (TextResponses, SubOrder, all_sandwiches, generate_user_info,
                                        closest_string_match_fuzzy, nearest_interval_time, find_nearest_stores)

from backend.selenium_app.order_sub_auto import order_sub, OrderSubFunctionDiagnostic


# Find/initialize the user
def get_user(session):
    phone_number = request.values.get("From")
    user = session.query(Users).filter(Users.phone_number == phone_number).first()
    if not user:
        user = Users(phone_number=phone_number,
                     name=None,
                     selected_store_address=None,
                     selected_store_name=None,
                     state='start')
        session.add(user)
        session.commit()
    return user


def start_action(*args):
    # Switches the user to the get_name state automatically
    # Might remove this later and just have the user initialized
    #   into the get_name state
    message_back = [f"Hey, welcome to Pubsub Py!",
                    state_info['get_name']['text_response']]

    return 'get_name', message_back


def get_name_action(body, session, user):
    # Get the user's name and save it to the database
    user.name = body
    session.commit()
    return 'get_store_location', state_info['get_store_location']['text_response']


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
           Distance: 14 meters
           
           ...
        """
        message_back = f"Here are the nearest stores I found to {body}\n :"
        for i, store in enumerate(nearest_stores):
            message_back += f"{i + 1}. {store['name']}\n " \
                            f"   Address: {store['address']}\n " \
                            f"   Distance: {round(store['distance'])} meters\n "

        message_back += "Which one would you like to order from? " \
                        "If none of these are correct, say 'redo' and we can go back a step."

        return "confirm_store", message_back
    else:
        return "get_location", "No stores found near that location, give me another location' \
                               'and I'll try to find some stores again."


def confirm_store_action(body, session, user):
    """
            There are two conditions that need to be checked here:
                1. If the user's input is a number, then it's referring to the index of the store
                    in the list of nearest stores. However, all texts come in as a string. Therefore
                    I use regex here to check if the string is a number.

                    If it is a number, then I convert it to an integer and use that to index the
                    list of nearest stores.

                2. If the user's input is a string, then it's referring to the name of the store.
                    I use fuzzy string matching to find the closest match to the user's input. By
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
        elif isinstance(body, str):
            store = closest_string_match_fuzzy(body, user.nearest_stores)

        if store is not None:
            user.selected_store_address = store['address']
            """
            The store name coming from the Google Places API always comes in as:
              'Publix Super Market at <store name>'
            
            This causes problems because I use the store name to select the store location
            from the Publix website HTML in Selenium. So, I use regex to remove the
            'Publix Super Market at ' part of the store name. 
            """
            remove_pattern = 'Publix Super Market at '
            user.selected_store_name = store['name'].replace(remove_pattern, '').strip()

            session.commit()
            message = f"Great! I'll remember that you want to order from {store['name']}.\n"

            messages = [(state_info['get_store_location']['text_response']), message]

            return 'default', messages

    else:
        message = ['I didn\'t get that, let\'s try that again. What\'s your preferred?',
                   'You can also say \'redo\' to search for a new location.']

        return 'confirm_store_location', message


def get_sale_action(body, session, *args):
    # Check if there are any sales today and return the corresponding message
    today = datetime.today().date()
    sales = session.query(SubDeal).filter(SubDeal.date == today).all()

    # If there is one sale, return the name of the sub
    match len(sales):
        case 1:
            message = "The " + sales[0].name.lower() + " is on sale today!"
        case 0:
            message = TextResponses().get_response("no_sale")
        case _:
            message = f"The {''.join([sale.name.lower() + ', ' for sale in sales])[:-2]}" \
                      f" are on sale today!"

    return 'default', message


def default_action(message, *args):
    # If the user input is recognized, initialize the default state
    if "order" in message:
        return 'order_sub', "You triggered the order sub action state. " \
                            "Say a sub name to order a sub. " \
                            "Say 'exit' to go back to the default state."
    else:
        return 'default', state_info['default']['text_response']


def order_sub_action(body, session, user, *args):
    if 'exit' in body:
        return 'default', ["you said exit, you're now in the default sate. say 'order' to order a sub."]

    if closest_string_match_fuzzy(item_to_match=body, match_possibilities_list=all_sandwiches) != "No match found":

        sandwich = closest_string_match_fuzzy(body, all_sandwiches)
        store_name = session.query(Users).filter(Users.phone_number == user.phone_number).first().selected_store_name
        store_address = session.query(Users).filter(
            Users.phone_number == user.phone_number).first().selected_store_address
        order_date = datetime.today().date().strftime("%A, %B %d, %Y")
        order_time = nearest_interval_time()

        first_name, last_name, email, phone_number = generate_user_info()

        order = SubOrder(
            requested_sub=sandwich,
            store_name=store_name,
            store_address=store_address,
            date_of_order=order_date,
            time_of_order=order_time,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number
        )

        def submit_order():
            order_sub(order, diagnostic=OrderSubFunctionDiagnostic())

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_in_executor(ThreadPoolExecutor(1), submit_order)
        loop.close()

        return 'order_sub', SubOrder.__str__(order)
    else:
        return 'order_sub', [
            f"you said: {body}, that is not a recognized sub name. say a sub name to order a sub. say 'exit' to go back to the"
            " default state"]


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
        'text_response': "nothing, replace this",
        'action': confirm_store_action,
        'next_states': ['get_sale']
    },
    'get_sale': {
        'text_response': TextResponses().get_response("help"),
        'action': get_sale_action,
        'next_states': ['default', 'order_sub']
    },
    'order_sub': {
        'text_response:': TextResponses().get_response("order_sub"),
        'action': order_sub_action,
        'next_states': ['default']
    },
    'default': {
        'text_response': TextResponses().get_response("default"),
        'action': default_action,
        'next_states': []
    }
}
