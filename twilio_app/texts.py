import os
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.twiml.messaging_response import Body, Message, Redirect, MessagingResponse

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

client = Client(account_sid, auth_token)

outgoing_number = os.getenv("TWILIO_OUTGOING_NUMBER")
incoming_number = os.getenv("TWILIO_INCOMING_NUMBER")
messaging_service_sid = os.getenv("TWILIO_MESSAGING_SERVICE_SID")


def send_message():

    client.messages \
        .create(
        messaging_service_sid=messaging_service_sid,
        body="Hello there!",
        to=outgoing_number
    )



