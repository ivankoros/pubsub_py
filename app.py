from flask import Flask, Response, request
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from main import SubDeal
from main import initialize_database

Base = declarative_base()

session = initialize_database()

app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    body = request.values.get("Body", "")

    resp = MessagingResponse()

    if "sale" in body.lower():
        today = datetime.now().date()
        print(today)

        sales = session.query(SubDeal).filter(SubDeal.date == today).all()

        if len(sales) == 1:
            for sale in sales:
                resp.message("The " + sale.name.lower() + " is on sale today.")
        elif len(sales) > 1:

            resp.message(f"The {''.join([sale.name.lower() + ', ' for sale in sales])[:-2]} are on sale today")
        else:
            resp.message("No subs on sale today.")
    else:
        resp.message("Sorry, I don't understand.")
        resp.message(f"Say 'sale' to see what subs are on sale today.")

    return Response(str(resp), mimetype="application/xml")


if __name__ == "__main__":
    app.run(debug=True)
