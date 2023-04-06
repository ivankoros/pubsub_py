import time
from flask import Flask, Response, request
from flask_restful import Resource, Api
from twilio.twiml.messaging_response import MessagingResponse
from backend.resources import initialize_database
from state_flow_mechanism import get_user, state_info

app = Flask(__name__)
api = Api(app)

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

    match next_state:
        case 'get_name':
            resp.message(f"Hey, welcome to Pubsub Py!")
            time.sleep(1)
            resp.message(message)
        case 'get_store_location':
            resp.message(f"Hey, {user.name}!")
            time.sleep(1)
            resp.message(message)
        case _:
            resp.message(message)

    return Response(str(resp), mimetype="application/xml")

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


api.add_resource(HelloWorld, '/')


if __name__ == "__main__":
    app.run(debug=True,
            host="0.0.0.0",
            port=5000)
