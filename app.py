from flask import Flask, Response, request
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import SubDeal  # Replace 'your_main_script' with the name of your main script file

app = Flask(__name__)

# Database configuration
engine = create_engine('sqlite:///sub_deal_data.db')
Session = sessionmaker(bind=engine)
session = Session()

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    body = request.values.get("Body", "")

    resp = MessagingResponse()

    if "sale" in body.lower():
        today = datetime.now().date()
        print(today)

        sales = session.query(SubDeal).filter(SubDeal.date == today).all()

        if sales:
            for sale in sales:
                resp.message("The " + sale.name + " is on sale today.")
        else:
            resp.message("No subs on sale today.")
    else:
        resp.message("Sorry, I don't understand.")

    return Response(str(resp), mimetype="application/xml")


if __name__ == "__main__":
    app.run(debug=True)
