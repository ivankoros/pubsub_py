from datetime import datetime
from flask import Flask, Response, request
from twilio.twiml.messaging_response import MessagingResponse

from resources import SubDeal
from resources import Users
from resources import initialize_database
from helpers import TextResponses

session = initialize_database()

app = Flask(__name__)

class SubRequest:
    def __init__(self, body):
        self.body = body

    def sub_name(self):
        return self.body.split(" ")[1].lower()


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    body = request.values.get("Body", "")

    resp = MessagingResponse()

    user = session.query(Users).filter(Users.phone_number == request.values.get("From")).first()
    if not user:
        user = Users(phone_number=request.values.get("From"),
                     name=None,
                     selected_store_address=None)
        session.add(user)
        session.commit()

        resp.message("Welcome to Pubsub Py!")
        resp.message("What's your name?")
        return Response(str(resp), mimetype="application/xml")

    if user.name is None:
        user.name = body
        session.commit()
        resp.message(f"Thanks, {user.name}! You are now registered with Pubsub Py!")
        resp.message(TextResponses().get_response("help"))
        return Response(str(resp), mimetype="application/xml")

    if user.selected_store_address is None:
        resp.message("You haven't selected a store yet!")


    if body.lower() in TextResponses().get_response("sale_prompt"):
        today = datetime.today().date()
        sales = session.query(SubDeal).filter(SubDeal.date == today).all()

        if len(sales) == 1:
            for sale in sales:
                resp.message("The " + sale.name.lower() + " is on sale today!")
        elif len(sales) > 1:
            resp.message(f"The {''.join([sale.name.lower() + ', ' for sale in sales])[:-2]}"
                         f" are on sale today!")
        else:
            resp.message(TextResponses().get_response("no_sale"))
    else:
        resp.message("Sorry, I don't understand.")
        resp.message(TextResponses().get_response("help"))

    return Response(str(resp), mimetype="application/xml")


if __name__ == "__main__":
    app.run(debug=True,
            host="0.0.0.0",
            port=5000)
