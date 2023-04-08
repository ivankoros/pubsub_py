import time
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

    # Initialize the user
    user = get_user(session)
    print(f"user says: {request.values.get('Body', '')}")

    # Get the action and required arguments from state_info
    action = state_info[user.state]['action']
    args = [request.values.get("Body", ""), session, user]

    # Execute the action and update the user state
    next_state, message = action(*args)
    user.state = next_state
    session.commit()

    # Send the response message
    resp = MessagingResponse()

    def reply_all_messages(messages_to_send):
        if type(messages_to_send) == str:
            resp.message(messages_to_send)
        else:
            for m in messages_to_send:
                resp.message(m)

    match next_state:
        case 'get_name':
            reply_all_messages(message)
        case 'get_store_location':
            resp.message(f"Hey, {user.name}!")
            time.sleep(1)
            resp.message(message)
        case _:
            print(f"message back to user: {message}")
            reply_all_messages(message)

    return Response(str(resp), mimetype="application/xml")

class UserData(Resource):
    # when this get function is called, it will query the database and return the results
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


api.add_resource(UserData, '/')

if __name__ == "__main__":
    app.run(debug=True,
            host="0.0.0.0",
            port=7000)
