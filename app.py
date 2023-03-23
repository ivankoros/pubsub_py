from flask import Flask, Response, request
from twilio.twiml.messaging_response import MessagingResponse
import main

app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    body = request.values.get("Body").lower()

    resp = MessagingResponse()

    if body == "whats on sale":
        sales = main.subs_on_sale
        for sale in sales:
            resp.message("The " + sale)

        resp.message(" there!")

    return Response(str(resp), mimetype="application/xml")


if __name__ == "__main__":
    app.run(debug=True)

