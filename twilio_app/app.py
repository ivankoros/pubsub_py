from datetime import datetime
from flask import Flask, Response, request
from twilio.twiml.messaging_response import MessagingResponse

from resources import SubDeal
from resources import Users
from resources import initialize_database
from twilio_app import TextResponses

app = Flask(__name__)


# Find/initialize the user
def get_user(session):
    user = session.query(Users).filter(Users.phone_number == request.values.get("From")).first()
    if not user:
        user = Users(phone_number=request.values.get("From"),
                     name=None,
                     selected_store_address=None,
                     state='start')
        session.add(user)
        session.commit()
    else:
        user = Users(phone_number=request.values.get("From"),
                     name=user.name,
                     selected_store_address=user.selected_store_address,
                     state=user.state)
    return user


def start_action(body, session):
    # Initialize the user in the database and prompt for their name

    return 'get_name', states['get_name']



def get_name_action(body, session, user):
    # Get the user's name and save it to the database
    user.name = body
    session.commit()
    return 'get_store_location', states['get_store_location']

def get_store_location_action(body, session, user):
    # This will later be replaced with a function that gets the user's geolocation
    #   and returns the nearest store using the find_nearest_stores function
    #   and the Google Maps api
    # But for now it just gets the user's address

    user.selected_store_address = body
    session.commit()
    return 'get_sale', states['get_sale']

def get_sale_action(body, session, user):
    # Check if there are any sales today and return the corresponding message
    today = datetime.today().date()
    sales = session.query(SubDeal).filter(SubDeal.date == today).all()

    # If there is one sale, return the name of the sub
    if len(sales) == 1:
        message = "The " + sales[0].name.lower() + " is on sale today!"

    # If there are multiple sales, return the names of the subs with commas
    elif len(sales) > 1:
        message = f"The {''.join([sale.name.lower() + ', ' for sale in sales])[:-2]}" \
                  f" are on sale today!"

    # If there are no sales, return the no sale message
    else:
        message = message = TextResponses().get_response("no_sale")

    # Go to the default state
    return 'default', message


def default_action(body, session, user):
    # If the user input is recognized, initialize the default state
    return 'default', states['default']


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    # Initalize database
    session = initialize_database()

    # Based on the telephone number, get the user from the database
    user = session.query(Users).filter(Users.phone_number == request.values.get("From")).first()

    # Initialize the user
    """
    This calls the custom get_user function, which either finds the user in the database
    and returns their info as a class, or creates a new user in the database and returns 
    their info as a class.
    """
    user = get_user(session)  # This is a class with attributes: phone_number, name, selected_store_address, state

    # Get the current state of the user
    current_user_state = user.state

    # Get the action corresponding to the user's current state
    action = state_machine[current_user_state]['action']
    """
    For example, if it's a new user, they're going to be in the 'start' state.
    
    The action corresponding to the 'start' state is the start_action function.
        - Found in the state_machine dictionary below
    """

    # Find the user's input (the "body" of their text message)
    body = request.values.get("Body", "")

    # What I'm doing here is using the action state as a function,
    # with inputs of the user's input and the database session
    next_state, message = action(body, session, user)
    user.state = next_state
    session.commit()  # Commit the user's new state to the database

    # Send the response message
    resp = MessagingResponse()
    resp.message(message)
    return Response(str(resp), mimetype="application/xml")


states = {
    'start': TextResponses().get_response("start"),
    'get_name': TextResponses().get_response("get_name"),
    'get_store_location': TextResponses().get_response("get_store_location"),
    'get_sale': TextResponses().get_response("get_sale"),
    'default': TextResponses().get_response("default"),
}

state_machine = {
    'start': {
        'action': start_action,
        'next_states': ['get_name']
    },
    'get_name': {
        'action': get_name_action,
        'next_states': ['get_store_location']
    },
    'get_store_location': {
        'action': get_store_location_action,
        'next_states': ['get_sale']
    },
    'get_sale': {
        'action': get_sale_action,
        'next_states': ['default']
    },
    'default': {
        'action': default_action,
        'next_states': []
    }
}

if __name__ == "__main__":
    app.run(debug=True,
            host="0.0.0.0",
            port=5000)
