from datetime import datetime
from flask import Flask, Response, request
from twilio.twiml.messaging_response import MessagingResponse

from resources import SubDeal
from resources import Users
from resources import initialize_database
from twilio_app import TextResponses


app = Flask(__name__)

def start_action(user_input, session):
    # Initialize the user in the database and prompt for their name
    user = session.query(Users).filter(Users.phone_number == request.values.get("From")).first()
    if not user:
        user = Users(phone_number=request.values.get("From"),
                     name=None,
                     selected_store_address=None,
                     state='start')
        session.add(user)
        session.commit()
        return 'get_name', states['get_name']
    else:
        return 'get_store_location', states['get_store_location']


def get_name_action(user_input, session):
    # Get the user's name and save it to the database
    user = session.query(Users).filter(Users.phone_number == request.values.get("From")).first()
    user.name = user_input
    session.commit()
    return 'get_store_location', states['get_store_location']


def get_store_location_action(user_input, session):
    # Find the nearest store based on the user's input and set it in the database
    user = session.query(Users).filter(Users.phone_number == request.values.get("From")).first()
    if user.selected_store_address is None:
        user.selected_store_address = user_input
        session.commit()
    return 'get_sale', states['get_sale']


def get_sale_action(user_input, session):
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


def default_action(user_input, session):
    # If the user input is recognized, initialize the default state
    return 'default', states['default']



@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    session = initialize_database()
    body = request.values.get("Body", "")

    user = session.query(Users).filter(Users.phone_number == request.values.get("From")).first()

    if not user:
        start_action("hi", session)

    current_state = session.query(Users).filter(Users.phone_number == request.values.get("From")).first().state
    # Get the action and next state based on the user's input and current state

    action = state_machine[current_state]['action']

    next_state, message = action(body, session)

    # Update the user's state in the database
    if user:
        user.state = next_state
        session.commit()

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
        'next_states': ['get_name', 'get_store_location']
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
