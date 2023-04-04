# Pubsub Py: Allowing automated, simple ordering for Publix deli subs through text with natural language processing

**Note: This project is a work in progress.**

Pubsub Py simplifies your Publix deli sub ordering process using natural language processing, allowing you to find deals of your local deli with one text and place an order with another.

Powered by Selenium 4, Pubsub Py scrapes your local deli's website daily and keeps you informed through text, courtesy of Twilio. Your t ext responses are cleaned and parsed using Spacy natural language processing, enabling one-text order placement. Supported by an AWS RDS MySQL cloud database and Docker for efficient, containerized runtimes, Pubsub Py grabbing a quick lunch easy on your wallet and mind.

This project has two main sections:

## Twilio and Twiml Messaging
- 



### Major Technologies Used

- **Selenium**: A Python library for web automation that enables autonomous browser control for automated web page interaction.
- **Twilio**: A cloud communications platform that automates incoming and outgoing SMS using its Python library.
- **SpaCy**: A Python library for natural language processing, used to extract meaning from text, such as customer preferences, to help create the perfect sandwich.
- **Docker**: A containerization platform that packages applications and their dependencies in lightweight, portable containers for easy deployment.

## Getting Started

These instructions will guide you through setting up Pubsub Py on your local machine.

### Prerequisites

- Python 3.8 or newer
- Docker installed
- A Twilio account

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pubsub_py.git
cd pubsub_py
```

2. Create a virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate
```


3. Install the required packages:
```python
pip install -r requirements.txt
```

4. Set up your environment variables:
```bash
export TWILIO_ACCOUNT_SID=your_account_sid
export TWILIO_AUTH_TOKEN=your_auth_token
export TWILIO_PHONE_NUMBER=your_twilio_phone_number
export YOUR_PHONE_NUMBER=your_phone_number
```


## Usage

Once everything is set up, send a text message to the Twilio phone number with your sandwich preferences. Pubsub Py will process your message, place an order for you, and send a confirmation text along with a reminder to pick up your sandwich.

## Contributing

We welcome contributions to this project. Please read the [CONTRIBUTING.md](CONTRIBUTING.md) for more information on how to contribute.

## License

This project is licensed under the MIT License. See the [LICENSE.md](LICENSE.md) file for details.

