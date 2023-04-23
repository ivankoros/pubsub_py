from flask import Flask, Response, request
from twilio.twiml.messaging_response import MessagingResponse
from backend.resources import initialize_database
from backend.twilio_app.state_flow_mechanism import get_user, state_info

app = Flask(__name__)

class Action:
    """
    Initialize an Action instance.

    :param action: Function to be executed.
    :param message: User's message (str).
    :param session: Database session.
    :param user: User instance.
    :param kwargs: Additional keyword arguments for the action function.
    """

    def __init__(self, action, message, session, user, **kwargs):
        self.action = action
        self.message = message
        self.session = session
        self.user = user
        self.kwargs = kwargs

    def execute(self):
        """
        Execute the specified action function with the given arguments.

        :return: Tuple containing the next state (str) and response message (str or list of str).
        """
        return self.action(self.message, self.session, self.user, **self.kwargs)

    @classmethod
    def process_user_input(cls, message, session, user):
        """
        Process user input and execute the corresponding action.

        :param user_state: User's current state (str).
        :param message: User's message (str).
        :param session: Database session.
        :param user: User instance.
        :return: Tuple containing the next state (str) and response message (str or list of str).
        """
        action_func = state_info[user.state]['action']
        action = cls(action_func, message, session, user)
        next_state, response_message = action.execute()
        return next_state, response_message


def reply_all_messages(messages_to_send, twilio_response_client):
    """Send all messages in the returned message list to the user.

    I have to check if the message is a string or a list (else) because
    the outgoing message can either a string or a list depending on the action
    state function.

    1. If it's a list, I need to iterate over it and send it as separate messages,
    which is the intended behavior.

    2. However, if it's a string and I try to iterate over it, it'll try to send
       every character as a separate message because strings are iterables themselves.
    """
    if isinstance(messages_to_send, str):
        twilio_response_client.message(messages_to_send)
    else:  # It's a list
        for m in messages_to_send:
            twilio_response_client.message(m)


@app.route("/sms", methods=['GET', 'POST'])
def handle_sms_request():
    """
    Handle SMS requests from Twilio and respond with the appropriate message.

    This function processes incoming SMS messages, executes the corresponding
    action based on the user's current state, and returns the response message.
    """

    session = initialize_database()
    user = get_user(session)
    message = request.values.get('Body', '')

    print(f"user says: {request.values.get('Body', '')}")

    # Process user input and execute the corresponding action
    next_state, response_message = Action.process_user_input(message=message,
                                                             session=session,
                                                             user=user)
    # Update the user's state in the database
    user.state = next_state
    session.commit()

    print(f"Message back to user: {response_message}")

    # Send the response message
    twilio_response_client = MessagingResponse()
    reply_all_messages(messages_to_send=response_message,
                       twilio_response_client=twilio_response_client)

    return Response(str(twilio_response_client), mimetype="application/xml")


if __name__ == "__main__":
    app.run(debug=True,
            host="0.0.0.0",
            port=8000)
