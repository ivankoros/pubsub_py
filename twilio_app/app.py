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

def get_sale_action(session, *args):
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
        message = TextResponses().get_response("no_sale")

    # Go to the default state
    return 'default', message


def default_action(*args):
    # If the user input is recognized, initialize the default state
    return 'default', state_info['default']['text_response']


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    # Initialize the database session
    session = initialize_database()

    # Initialize the user
    user = get_user(session)

    # Get the action and required arguments from state_info
    action = state_info[user.state]['action']
    args = [request.values.get("Body", ""), session, user]

    # Execute the action and update the user state
    next_state, message = action(*args)
    user.state = next_state
    session.commit()

    # Send the response message
    resp = MessagingResponse()
    resp.message(message)
    return Response(str(resp), mimetype="application/xml")

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
        'text_response': TextResponses().get_response("get_sale"),
        'action': get_sale_action,
        'next_states': ['default']
    },
    'default': {
        'text_response': TextResponses().get_response("default"),
        'action': default_action,
        'next_states': []
    }
}



if __name__ == "__main__":
    app.run(debug=True,
            host="0.0.0.0",
            port=5000)
