from flask import Flask, Response, request
from twilio.twiml.messaging_response import MessagingResponse
import random

app = Flask(__name__)


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    body = request.values.get("Body", "")

    resp = MessagingResponse()

    if "sale" in body.lower():
        sales = ["Italian Sub", "Ham Sub", "Turkey Sub", "Veggie Sub", "Tuna Sub", "Meatball Sub"]
        resp.message("The " + random.choice(sales))
        resp.message("The " + random.choice(sales))
        resp.message("The " + random.choice(sales))
    else:
        resp.message("Sorry, I don't understand.")

    return Response(str(resp), mimetype="application/xml")


if __name__ == "__main__":
    app.run(debug=True)
