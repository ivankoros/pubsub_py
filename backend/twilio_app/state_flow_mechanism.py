import asyncio
from datetime import datetime
from flask import request
from concurrent.futures import ThreadPoolExecutor
from backend.nlp import find_closest_sandwich_sk
import re
import random

from backend.resources import SubDeal
from backend.resources import Users
from backend.twilio_app.helpers import (TextResponses, SubOrder, all_sandwiches, generate_user_info,
                                        nearest_interval_time, find_nearest_stores, find_zip)
from backend.twilio_app.publix_api import query_deals

from backend.selenium_app.order_sub_auto import order_sub, OrderSubFunctionDiagnostic


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
                     selected_store_address=None,
                     selected_store_name=None,
                     selected_store_id=None,
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
        else:
            store = find_closest_sandwich_sk(body, [store['name'] for store in user.nearest_stores])
            store = next((s for s in user.nearest_stores if s['name'] == store), None)

        if store:
            longitude, latitude = store['longitude'], store['latitude']
            zip_code = find_zip(longitude, latitude)

            store_name = store['name'].replace('Publix Super Market at ', '').strip()

            user.selected_store = {
                'name': store_name,
                'address': store['address'],
                'zip_code': zip_code,

            }

            """
            The store name coming from the Google Places API always comes in as:
              'Publix Super Market at <store name>'
            
            This causes problems because I use the store name to select the store location
            from the Publix website HTML in Selenium. So, I use regex to remove the
            'Publix Super Market at ' part of the store name. 
            """

            session.commit()

            messages = [f"Great! I'll remember that you want to order from {store['name']}.",
                        "You're all set! You can ask me what's on sale to get deals from "
                        "your store or say 'order' to put in an order."]

            return 'default', messages

        else:
            message = ["I didn't get that. You can give a number (1) or text confirmation (Yea, St. John's Town Center)",
                       "You can also say 'redo' to search for a new location."]
            return 'confirm_store', message
    else:
        message = ["Okay, let's try that again. Give me a location and I'll find the nearest stores."]
        return 'get_store_location', message



def get_sale_action(body, session, *args):
    pass


def default_action(message, session, user, *args):
    # If the user input is recognized, initialize the default state
    if "order" in message.lower():
        return 'order_sub', ["You're all set to order for quick pickup. Give me an order "
                             "and it'll be ready for pickup in 30 minutes.\n\n"
                             "Example: 'Let me get a hot meatball sub with provolone'",
                             "You can also say 'exit' to go back."]

    elif "sale" in message.lower() or "deal" in message.lower():
        # Check if there are any sales today and return the corresponding message
        today_sales = session.query(SubDeal).filter(SubDeal.date == datetime.today().date()).all()

        if not today_sales:
            zip = user.selected_store_address.split(',')[-1].strip()
            query_deals(zip)

            today_sales = session.query(SubDeal).filter(SubDeal.date == datetime.today().date()).all()

        if len(today_sales) == 1:
            message = "The " + today_sales[0].name.lower() + " is on sale today!"
        else:
            message = f"The {', '.join([sale.name.lower() for sale in today_sales][:-1])}, " \
                      f"and {today_sales[-1].name.lower()} are on sale today!"

        messages = ["Let's see what's on sale today!", message]

        return 'default', messages

    else:
        return 'default', state_info['default']['text_response']


def order_sub_action(body, session, user, *args):
    """
    This is the main important ordering function. It's called when the user is in the 'order_sub'
    state.

    1. If the user says 'exit', then they are taken back to the default state.

    2. If the user does not say exit, I treat the user's input as a potential sub name
        they're trying to say, and use fuzzy logic string matching to compare it against
        all the sub names in the database. If there is a match above the cutoff (set default at 70%),
        then I return the name of the sub. Otherwise, I return 'No match found', and prompt the user
        to try again.

    3. If there is a match, I create a class with the order information
        - I use the user's sandwich request for the sub name
        - I randomly generate a first name, last name, phone number, and email for the order
        - I use the user's preferred store name and address to select the store location from the
            Publix website HTML in Selenium.
        - I generate the date as today and the time with my custom function to find the soonest
            available time Publix will have. This is described below with examples

    4. I then pass this SubOrder class with all the order info needed into the order_sub function,
        which automates the ordering with Selenium. However, this takes about 40 seconds to run,
        so I use the threading module to run it in a separate thread.

    5. Feedback of the user's confirmed order is returned to the user instantly after ordering.
        Because I've passed the order_sub function into a separate thread, the user doesn't have
        to wait for the order to be placed. All the order info that I would need to send to the
        user is saved in the SubOrder class, so I can just return that info to the user with the
        __str__ method set up in the class.


    :param body: The user's text
    :param session:  The database session (MySQL)
    :param user:  The user's database entry
    :param args:  Any other arguments
    :return:  Order feedback message
    """
    if 'exit' in body:
        return 'default', ["you said exit, you're now in the default sate. say 'order' to order a sub."]

    if find_closest_sandwich_sk(item_to_match=body, match_possibilities_list=all_sandwiches) != "No match found":

        sandwich = find_closest_sandwich_sk(body, all_sandwiches)
        store_name = session.query(Users).filter(Users.phone_number == user.phone_number).first().selected_store_name
        store_address = session.query(Users).filter(
            Users.phone_number == user.phone_number).first().selected_store_address
        order_date = datetime.today().date().strftime("%A, %B %d, %Y")
        order_time = nearest_interval_time()

        """ What is nearest_interval_time()?
        
            This is my custom function to get the nearest 30 minute interval 
            with a five minute buffer. This is the time that the Publix will 
            Schedule the order for.
            
            This is not arbitrary, I figured out how the time for soonest order
            possible is calculated by Publix and this is my implementation of it.
            
            Examples:
             - ordering at 12:02 PM will give a pickup time of 12:30 PM
             - ordering at 12:06 PM will give a pickup time of 12:40 PM
                
        """

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
            order_sub(self=order,
                      diagnostic=OrderSubFunctionDiagnostic())

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
