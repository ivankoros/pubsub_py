from flask import Flask, Response, request
from flask_restful import Resource, Api
from twilio.twiml.messaging_response import MessagingResponse
from backend.resources import initialize_database
from backend.twilio_app.state_flow_mechanism import get_user, state_info
from backend.resources import Users

app = Flask(__name__)
api = Api(app)


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    # Initialize the database session
    session = initialize_database()

    """Initialize the user object
    
    If the user is new, create a new user object and add it to the database.
    If the user is not new, get the user object from the database with their
    info such as their preferred store location, name, and most importantly
    state - 'get_name', 'get_store_location', or 'get_order', remebering
    where the user left off.
    
    """
    user = get_user(session)
    print(f"user says: {request.values.get('Body', '')}")

    """Use my state flow mechanism to determine what to do next:
        - What message to send back to the user?
        - What state can the user come and go from?
        - What action should be taken when the user sends a message?
        
        Here, 'action' is a dynamic function that changes based on the users
        state. It's defined in state_flow_mechanism.py under the state_info
        dictionary. The function of their current state is called with the
        user's message (body), the database session (session), and the user
        object (user).
        
        I now define the arguments for the action function, taking these
        three arguments:
            - message: the user's message
            - session: the database session
            - user: the user object
        
        Then, I pass the arguments into the action functions, with 
        a star in front of the arguments. This is called 'unpacking' and
        it allows me to pass in the arguments as a list. I do this because
        each action function may take a different number of arguments, and
        this way I don't have to change the code for each action function if
        I choose to add or remove arguments.
        
        Passing the arguments into he action we pull from the flow state mechanism
        based off the user's state, it always returns 2 things: 
            1. the state the user
            2. should transition to and and the message to send back to them.
        
         - next_state, message = action(*args) 
         - next_state: the state the user should transition to
         - message: the message to send back to the user
            
        Example:
        The user texts in for the firs time:
        
        1. Their state is initialized as 'start' from the get_user() function.
        2. The action for the get_name state is pulled from the state_info dictionary.
          The 'start' state corresponds to the 'start_action' function.
          
            action = state_info['start']['action'] -->
            action = start_action()
            
        3.  The action function is called with the user's message, the database session,
            and the user object. The start_action function uses its own logic to greet the
            user and ask for their name. It returns the next state as the 'get_name' state
            and the message as the greeting and name request. 
            
            next_state, message = action(*args) -->
            next_state, message = start_action(message, session, user)
        
        4. The user's state is updated to the 'get_name' state in the database.
        
        5. A MessagingResponse object is created to send back to the user, which
           is a Twilio object that allows us to send back a message to the user.
           
           The message object is set up with all the messages coming from the action
           function, is returned to the Flask app through the Twiml Response object
           through xml as a web response.
           
           I have wherever the Flask app is hosted as a webhook for the Twilio number
           through the Twilio console, so my outputted responses first are sent to my
           Flask app, which is being listened to by Twilio, and is then sent back to
           the user.      
        
    """
    action = state_info[user.state]['action']

    args = [request.values.get("Body", ""), session, user]

    # Execute the action and update the user state
    next_state, message = action(*args)
    user.state = next_state
    session.commit()

    # Send the response message
    resp = MessagingResponse()
    """Send all messages in the returned message list to the user.
    
    I have to check if the message is a string or a list (else) because
    the outgoing message can either a string or a list depending on the action
    state function.
    
    1. If its a list, I need to iterate over it and send it as separate messages,
    which is the intended behavior.
    
    2. However, if its a string and I try to iterate over it, it'll try to send
       every character as a separate message because strings are iterables themselves.
    """

    def reply_all_messages(messages_to_send):
        if isinstance(messages_to_send, str):
            resp.message(messages_to_send)
        else:
            for m in messages_to_send:
                resp.message(m)

    print(f"message back to user: {message}")
    reply_all_messages(message)

    return Response(str(resp), mimetype="application/xml")


class UserData(Resource):
    """Rest API

        This is the rest API I will use to server my React app later.

    """

    def get(self):
        session = initialize_database()
        users = session.query(Users).all()

        users_dict = {"users": []}

        for user in users:
            user_dict = {
                "id": user.id,
                "phone_number": user.phone_number,
                "name": user.name,
                "selected_store_address": user.selected_store_address,
                "state": user.state
            }
            users_dict["users"].append(user_dict)
        return users_dict


# Adding the API on the '/' endpoint for requests to access.
api.add_resource(UserData, '/')

if __name__ == "__main__":
    app.run(debug=True,
            host="0.0.0.0",
            port=8000)
