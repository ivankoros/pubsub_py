import time
from datetime import datetime, timedelta
from flask import Flask, Response, request

from backend.resources import SubDeal
from backend.resources import Users
from backend.twilio_app.helpers import (TextResponses, SubOrder, all_sandwiches, generate_user_info,
                                        find_closest_sandwich, nearest_interval_time)

from backend.selenium_app.order_sub_auto import order_sub, OrderSubFunctionDiagnostic


# Find/initialize the user
def get_user(session):
    phone_number = request.values.get("From")
    user = session.query(Users).filter(Users.phone_number == phone_number).first()
    if not user:
        user = Users(phone_number=phone_number,
                     name=None,
                     selected_store_address=None,
                     state='start')
        session.add(user)
        session.commit()
    return user


def start_action(*args):
    # Switches the user to the get_name state automatically
    # Might remove this later and just have the user initialized
    #   into the get_name state
    return 'get_name', state_info['get_name']['text_response']


def get_name_action(body, session, user):
    # Get the user's name and save it to the database
    user.name = body
    session.commit()
    return 'get_store_location', state_info['get_store_location']['text_response']


def get_store_location_action(body, session, user):
    # This will later be replaced with a function that gets the user's geolocation
    #   and returns the nearest store using the find_nearest_stores function
    #   and the Google Maps api
    # But for now it just gets the user's address

    user.selected_store_address = body
    session.commit()
    return 'get_sale', state_info['get_sale']['text_response']


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
        return 'default', "you said exit, you're now in the default sate. say 'order' to order a sub."

    if find_closest_sandwich(body, all_sandwiches) != "No match found":

        sandwich = find_closest_sandwich(body, all_sandwiches)
        store_name = session.query(Users).filter(Users.phone_number == user.phone_number).first().selected_store_address
        order_date = datetime.today().date().strftime("%A, %B %d, %Y")
        order_time = nearest_interval_time()

        first_name, last_name, email, phone_number = generate_user_info()

        order = SubOrder(
            requested_sub=sandwich,
            store_name=store_name,
            date_of_order=order_date,
            time_of_order = order_time,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number

        )

        return 'order_sub', SubOrder.__str__(order)
    else:
        return 'order_sub', f"you said: {body}, that is not a recognized sub name. say a sub name to order a sub. say 'exit' to go back to the" \
                            " default state"


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
